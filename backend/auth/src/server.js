require("dotenv").config();

const express = require("express");
const session = require("express-session");
const jwt = require("jsonwebtoken");
const cors = require("cors");
const { Zoogle } = require("zoogle");

const app = express();

const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) {
  console.error("Missing JWT_SECRET in environment");
  process.exit(1);
}

app.use(express.json());
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

// Zoogle setup
const zoogle = new Zoogle({
  providers: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackUrl:
        process.env.CALLBACK_URL ||
        `http://localhost:${PORT}/auth/google/callback`,
      scope: ["profile", "email"],
    },
  },
});

// Tiny helper: generate JWT
function signToken(payload) {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: "1h" });
}

// Middleware to protect routes
function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization || "";
  const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : null;
  if (!token) return res.status(401).json({ error: "Missing token" });
  jwt.verify(token, JWT_SECRET, (err, decoded) => {
    if (err) return res.status(401).json({ error: "Invalid token" });
    req.user = decoded;
    next();
  });
}

// Initiate Google OAuth
app.get("/auth/google", (req, res) => {
  try {
    const url = zoogle.getAuthUrl("google");
    // Save state in session if provided by zoogle
    if (zoogle.state) req.session.zoogleState = zoogle.state;
    res.redirect(url);
  } catch (err) {
    console.error("Failed to initiate OAuth", err);
    res.status(500).send("Failed to initiate OAuth");
  }
});

// OAuth callback
app.get("/auth/google/callback", async (req, res) => {
  try {
    const { code, state } = req.query;
    // Optionally verify state from session
    if (req.session.zoogleState && state && req.session.zoogleState !== state) {
      return res.status(400).send("Invalid OAuth state");
    }

    const profile = await zoogle.getProfile("google", {
      code,
      callbackUrl: zoogle.config.providers.google.callbackUrl,
    });
    // profile expected to contain id, displayName, emails, photos
    const user = {
      id: profile.id,
      name:
        profile.displayName ||
        (profile.name &&
          `${profile.name.givenName} ${profile.name.familyName}`) ||
        "Unknown",
      email: Array.isArray(profile.emails)
        ? profile.emails[0].value
        : profile.email || "",
      picture: Array.isArray(profile.photos)
        ? profile.photos[0].value
        : profile.picture || "",
      provider: "google",
    };

    // Create JWT
    const token = signToken({
      sub: user.id,
      email: user.email,
      name: user.name,
    });

    // Save minimal session info
    req.session.user = { id: user.id, name: user.name, email: user.email };

    // Redirect to frontend with token as fragment or set cookie as desired
    const redirectTo =
      (process.env.FRONTEND_CALLBACK || "http://localhost:8080") +
      `#token=${token}`;
    res.redirect(redirectTo);
  } catch (err) {
    console.error("OAuth callback error", err);
    res.status(500).send("OAuth callback error");
  }
});

// Verify token endpoint
app.post("/auth/verify", (req, res) => {
  const { token } = req.body;
  if (!token) return res.status(400).json({ error: "token required" });
  jwt.verify(token, JWT_SECRET, (err, decoded) => {
    if (err)
      return res.status(401).json({ valid: false, error: "Invalid token" });
    res.json({ valid: true, payload: decoded });
  });
});

// Protected profile route
app.get("/auth/profile", requireAuth, (req, res) => {
  // Return the data stored in the JWT
  res.json({ profile: req.user });
});

// Logout
app.post("/auth/logout", (req, res) => {
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
