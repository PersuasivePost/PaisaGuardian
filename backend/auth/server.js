require("dotenv").config();

const express = require("express");
const session = require("express-session");
const jwt = require("jsonwebtoken");
const cors = require("cors");
const cookieParser = require("cookie-parser");
// zoogle exports a default configured instance and helpers
const zoogleModule = require("zoogle");
const zoogle = zoogleModule.default || zoogleModule;
const { commonHandlers } = require("zoogle");
const { PrismaClient } = require("@prisma/client");
const crypto = require("crypto");

const app = express();

const PORT = process.env.PORT || 3000;
// Prefer asymmetric keys so other services (FastAPI) can verify using the public key
const PRIVATE_KEY = process.env.PRIVATE_KEY || null;
const PUBLIC_KEY = process.env.PUBLIC_KEY || null;
const JWKS_KID = process.env.JWKS_KID || "auth-key-1";

let privateKeyPem = PRIVATE_KEY;
let publicKeyPem = PUBLIC_KEY;
if (!privateKeyPem || !publicKeyPem) {
  console.warn(
    "No PRIVATE_KEY/PUBLIC_KEY found in env — generating ephemeral RSA keypair (not persistent)."
  );
  const { privateKey, publicKey } = crypto.generateKeyPairSync("rsa", {
    modulusLength: 2048,
  });
  privateKeyPem = privateKey.export({ type: "pkcs1", format: "pem" });
  publicKeyPem = publicKey.export({ type: "pkcs1", format: "pem" });
  console.warn(
    "Ephemeral keypair generated — save these to env for persistent tokens."
  );
}

app.use(express.json());
app.use(cookieParser());
app.use(
  cors({
    origin: process.env.FRONTEND_ORIGIN || "http://localhost:8080",
    credentials: true,
  })
);

app.use(
  session({
    secret: process.env.SESSION_SECRET || "dev_session_secret",
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false },
  })
);

let prisma = null;
if (process.env.DATABASE_URL) {
  try {
    // new PrismaClient() may throw if the generated client is missing or incompatible.
    prisma = new PrismaClient();
    prisma
      .$connect()
      .then(() => console.log("Prisma connected to DB"))
      .catch((err) => console.error("Prisma connection error:", err));
  } catch (err) {
    console.error(
      "Prisma client failed to initialize (client may not be generated):",
      err.message || err
    );
    prisma = null;
  }
} else {
  console.warn("No DATABASE_URL provided; Prisma client not initialized.");
}

// Tiny helper: generate JWT
function signToken(payload) {
  // RS256 signing using private key
  return jwt.sign(payload, privateKeyPem, {
    algorithm: "RS256",
    expiresIn: "1h",
    keyid: JWKS_KID,
  });
}

// Middleware to protect routes
function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization || "";
  const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : null;
  if (!token) return res.status(401).json({ error: "Missing token" });
  jwt.verify(token, publicKeyPem, { algorithms: ["RS256"] }, (err, decoded) => {
    if (err) return res.status(401).json({ error: "Invalid token" });
    req.user = decoded;
    next();
  });
}

// Configure zoogle (Google OAuth helper)
zoogle.configure({
  google: {
    clientId: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL:
      process.env.CALLBACK_URL ||
      `http://localhost:${PORT}/auth/google/callback`,
  },
  jwt: {
    // jwt block here is informational for zoogle; we will sign tokens ourselves with RS256
    secret: "use-rs256-private-key",
    expiresIn: "1h",
  },
  // findOrCreateUser must return the user record the app will treat as the principal
  findOrCreateUser: async (googleProfile) => {
    // googleProfile shape from zoogle.oauth.getUserInfo: { id, email, name, picture }
    const appUser = {
      provider: "google",
      providerId: googleProfile.id,
      email: googleProfile.email || null,
      name: googleProfile.name || null,
      picture: googleProfile.picture || null,
    };
    if (!prisma) {
      // No DB: return a minimal user object
      return {
        id: appUser.providerId,
        email: appUser.email,
        name: appUser.name,
      };
    }
    // Persist with Prisma
    const dbUser = await prisma.user.upsert({
      where: { providerId: appUser.providerId },
      update: {
        email: appUser.email,
        name: appUser.name,
        picture: appUser.picture,
      },
      create: appUser,
    });
    return { id: dbUser.id, email: dbUser.email, name: dbUser.name };
  },
  // custom success handler: sign RS256 token, set httpOnly cookie, then redirect
  onSuccess: async (user, token, req, res) => {
    // `user` is the object returned from findOrCreateUser
    const payload = {
      sub: user.id,
      email: user.email,
      name: user.name,
      permissions: user.permissions || [],
    };
    // Access token 24h
    const accessToken = jwt.sign(payload, privateKeyPem, {
      algorithm: "RS256",
      expiresIn: "24h",
      keyid: JWKS_KID,
    });
    // Create refresh token (longer lived, opaque)
    const refreshTokenValue = crypto.randomBytes(48).toString("hex");
    const refreshExpires = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days

    if (prisma) {
      try {
        await prisma.refreshToken.create({
          data: {
            token: refreshTokenValue,
            userId: user.id,
            expiresAt: refreshExpires,
          },
        });
      } catch (e) {
        console.error("Failed to persist refresh token", e.message || e);
      }
    }

    // Set secure cookies
    res.cookie("auth_token", accessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      maxAge: 24 * 60 * 60 * 1000,
    });
    res.cookie("refresh_token", refreshTokenValue, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      maxAge: 30 * 24 * 60 * 60 * 1000,
    });
    // Redirect to frontend and include token in hash for client-side JS if desired
    const redirectTo =
      (process.env.FRONTEND_CALLBACK || "http://localhost:8080") +
      `#token=${accessToken}`;
    res.redirect(redirectTo);
  },
});

// Expose the public key so other services (FastAPI) can fetch it and verify tokens
app.get("/auth/public_key", (req, res) => {
  res.type("text/plain").send(publicKeyPem);
});

// Alternative: return JWKS (simple static format)
app.get("/auth/.well-known/jwks.json", (req, res) => {
  // For simplicity return the public key PEM under a single key id.
  res.json({
    keys: [
      { kid: JWKS_KID, kty: "RSA", use: "sig", alg: "RS256", publicKeyPem },
    ],
  });
});

app.use("/auth/google", zoogle.routes);
app.get("/auth/google", (req, res) => res.redirect("/auth/google/login"));

// Google ID token verification endpoint for mobile app
app.post("/auth/google/verify", async (req, res) => {
  try {
    const { idToken, email, name, picture } = req.body;

    if (!idToken) {
      return res.status(400).json({ error: "idToken required" });
    }

    // Verify the Google ID token
    const { OAuth2Client } = require("google-auth-library");
    const client = new OAuth2Client(process.env.GOOGLE_CLIENT_ID);

    let ticket;
    try {
      ticket = await client.verifyIdToken({
        idToken: idToken,
        audience: process.env.GOOGLE_CLIENT_ID,
      });
    } catch (verifyError) {
      console.error("ID token verification failed:", verifyError.message);
      return res.status(401).json({ error: "Invalid ID token" });
    }

    const payload = ticket.getPayload();
    const googleUserId = payload["sub"];

    // Create/update user
    const appUser = {
      provider: "google",
      providerId: googleUserId,
      email: email || payload["email"],
      name: name || payload["name"],
      picture: picture || payload["picture"],
    };

    let user;
    if (!prisma) {
      // No DB: return a minimal user object
      user = {
        id: appUser.providerId,
        email: appUser.email,
        name: appUser.name,
      };
    } else {
      // Persist with Prisma
      user = await prisma.user.upsert({
        where: { providerId: appUser.providerId },
        update: {
          email: appUser.email,
          name: appUser.name,
          picture: appUser.picture,
        },
        create: appUser,
      });
    }

    // Create access token
    const tokenPayload = {
      sub: user.id,
      email: user.email,
      name: user.name,
      permissions: user.permissions || [],
    };

    const accessToken = jwt.sign(tokenPayload, privateKeyPem, {
      algorithm: "RS256",
      expiresIn: "24h",
      keyid: JWKS_KID,
    });

    // Create refresh token
    const refreshTokenValue = crypto.randomBytes(48).toString("hex");
    const refreshExpires = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days

    if (prisma) {
      try {
        await prisma.refreshToken.create({
          data: {
            token: refreshTokenValue,
            userId: user.id,
            expiresAt: refreshExpires,
          },
        });
      } catch (e) {
        console.error("Failed to persist refresh token", e.message || e);
      }
    }

    res.json({
      accessToken,
      refreshToken: refreshTokenValue,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
      },
    });
  } catch (error) {
    console.error("Google verify error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Verify token endpoint - supports both body and Authorization header
app.post("/auth/verify", (req, res) => {
  console.log("📝 /auth/verify called");
  console.log("   Headers:", JSON.stringify(req.headers, null, 2));
  console.log("   Body:", JSON.stringify(req.body, null, 2));

  // Check Authorization header first, then body
  const authHeader = req.headers.authorization || "";
  const tokenFromHeader = authHeader.startsWith("Bearer ")
    ? authHeader.slice(7)
    : null;
  const token = tokenFromHeader || req.body.token;

  console.log("   Token source:", tokenFromHeader ? "Header" : "Body");
  console.log(
    "   Token (first 20):",
    token ? token.substring(0, 20) + "..." : "NONE"
  );

  if (!token) {
    console.log("   ✗ No token provided");
    return res.status(400).json({ error: "token required" });
  }

  jwt.verify(token, publicKeyPem, { algorithms: ["RS256"] }, (err, decoded) => {
    if (err) {
      console.log("   ✗ Token verification failed:", err.message);
      return res.status(401).json({ valid: false, error: "Invalid token" });
    }
    console.log("   ✓ Token verified for user:", decoded.sub);
    res.json({
      valid: true,
      userId: decoded.sub,
      email: decoded.email,
      name: decoded.name,
    });
  });
});

// Exchange refresh token for a new access token
app.post("/auth/refresh", async (req, res) => {
  const refreshToken = req.cookies?.refresh_token || req.body?.refresh_token;
  if (!refreshToken)
    return res.status(400).json({ error: "refresh_token required" });
  if (!prisma) return res.status(503).json({ error: "DB not available" });

  try {
    const record = await prisma.refreshToken.findUnique({
      where: { token: refreshToken },
    });
    if (!record || record.revoked)
      return res.status(401).json({ error: "Invalid refresh token" });
    if (new Date(record.expiresAt) < new Date())
      return res.status(401).json({ error: "Refresh token expired" });

    const user = await prisma.user.findUnique({ where: { id: record.userId } });
    if (!user) return res.status(404).json({ error: "User not found" });

    const payload = {
      sub: user.id,
      email: user.email,
      name: user.name,
      permissions: user.permissions || [],
    };
    const newAccess = jwt.sign(payload, privateKeyPem, {
      algorithm: "RS256",
      expiresIn: "24h",
      keyid: JWKS_KID,
    });

    res.cookie("auth_token", newAccess, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      maxAge: 24 * 60 * 60 * 1000,
    });
    res.json({ accessToken: newAccess });
  } catch (e) {
    console.error("Refresh error", e.message || e);
    res.status(500).json({ error: "Server error" });
  }
});

// Protected profile route
app.get("/auth/profile", requireAuth, (req, res) => {
  // Return the data stored in the JWT
  res.json({ profile: req.user });
});

// Logout
app.post("/logout", (req, res) => {
  const refreshToken = req.cookies?.refresh_token || req.body?.refresh_token;
  if (refreshToken && prisma) {
    prisma.refreshToken
      .updateMany({ where: { token: refreshToken }, data: { revoked: true } })
      .catch((e) =>
        console.error("Failed to revoke refresh token", e.message || e)
      );
  }
  // Clear cookies
  res.clearCookie("auth_token");
  res.clearCookie("refresh_token");
  req.session.destroy((err) => {
    if (err) return res.status(500).json({ error: "Failed to logout" });
    res.json({ ok: true });
  });
});

// Basic health route
app.get("/", (req, res) => res.send("Auth server running"));

// Error handler
app.use((err, req, res, next) => {
  console.error("Unhandled error", err);
  res.status(500).json({ error: "Internal server error" });
});

app.listen(PORT, () => console.log(`Auth server listening on ${PORT}`));
