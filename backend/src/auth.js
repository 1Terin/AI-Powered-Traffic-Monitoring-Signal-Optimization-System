const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const router = express.Router();

// In-memory device store (replace with DB in production)
const devices = new Map();
const JWT_SECRET = process.env.JWT_SECRET || 'replace-with-secure-secret';

// Register a device and return credentials (deviceId, secret, token)
router.post('/register', async (req, res) => {
  const { deviceId } = req.body;
  if (!deviceId) return res.status(400).json({ error: 'deviceId required' });

  const secret = Math.random().toString(36).slice(2, 12);
  const hashed = await bcrypt.hash(secret, 8);
  devices.set(deviceId, { secret: hashed });

  const token = jwt.sign({ deviceId }, JWT_SECRET, { expiresIn: '30d' });
  res.json({ deviceId, secret, token });
});

// auth middleware for REST endpoints
function verifyDeviceToken(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth) return res.status(401).json({ error: 'missing auth' });
  const parts = auth.split(' ');
  if (parts.length !== 2) return res.status(401).json({ error: 'invalid auth header' });
  const token = parts[1];
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.device = payload;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'invalid token' });
  }
}

module.exports = { router, verifyDeviceToken };
