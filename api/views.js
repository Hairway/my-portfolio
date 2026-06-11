// Visitor counter — Vercel Node serverless function (no external deps).
//
// Counts UNIQUE visitors all-time. Each visitor's IP is hashed (raw IPs are
// never stored). The owner's IP is excluded, and the running total is returned
// only to the owner (the page decides whether to display it).
//
// Storage: Upstash Redis via its REST API. Env vars are provided automatically
// when the Upstash integration is connected to the project:
//   UPSTASH_REDIS_REST_URL / UPSTASH_REDIS_REST_TOKEN  (or the KV_* equivalents)
// Plus one secret we set ourselves:
//   VIEWS_ADMIN_TOKEN  — the owner appends #stats=<token> once to reveal the count.

const crypto = require('node:crypto');

const REST_URL = process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL;
const REST_TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN;
const ADMIN_TOKEN = process.env.VIEWS_ADMIN_TOKEN || '';

const VISITORS = 'views:visitors'; // set of hashed visitor IPs  -> SCARD = total
const OWNERS = 'views:owners';     // set of hashed owner IPs (never counted)
const SALT = 'dimafomin-portfolio-v1';

// Run one or more Redis commands through the Upstash REST pipeline endpoint.
async function pipe(commands) {
  const res = await fetch(`${REST_URL}/pipeline`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${REST_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(commands),
  });
  if (!res.ok) throw new Error('redis ' + res.status);
  return res.json(); // -> [{ result }, ...]
}

function ipHash(req) {
  const xff = (req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  const ip = xff || (req.socket && req.socket.remoteAddress) || 'unknown';
  return crypto.createHash('sha256').update(ip + '|' + SALT).digest('hex').slice(0, 24);
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');

  if (!REST_URL || !REST_TOKEN) {
    res.status(200).json({ count: null, error: 'storage-not-configured' });
    return;
  }

  try {
    const hash = ipHash(req);
    const token = req.query && req.query.admin;
    const isAdminRequest = token && ADMIN_TOKEN && token === ADMIN_TOKEN;

    if (isAdminRequest) {
      // Owner: remember this IP as owner and make sure it isn't counted.
      const out = await pipe([
        ['SADD', OWNERS, hash],
        ['SREM', VISITORS, hash],
        ['SCARD', VISITORS],
      ]);
      res.status(200).json({ count: out[2].result, admin: true });
      return;
    }

    // Normal visitor: count once, unless this IP is a known owner.
    const owner = await pipe([['SISMEMBER', OWNERS, hash]]);
    if (!owner[0].result) {
      await pipe([['SADD', VISITORS, hash]]);
    }
    const out = await pipe([['SCARD', VISITORS]]);
    res.status(200).json({ count: out[0].result });
  } catch (e) {
    res.status(200).json({ count: null, error: 'temporary' });
  }
};
