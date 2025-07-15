const express = require("express");
const router = express.Router();
const pool = require("../db");

// Get all messages
router.get("/", async (req, res) => {
  try {
    const allMessages = await pool.query("SELECT * FROM messages ORDER BY id DESC");
    res.json(allMessages.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get a single message
router.get("/:id", async (req, res) => {
  const { id } = req.params;
  try {
    const message = await pool.query("SELECT * FROM messages WHERE id = $1", [id]);
    if (message.rows.length === 0) {
      return res.status(404).json({ error: "Message not found" });
    }
    res.json(message.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get all messages for a specific client
router.get("/client/:clientId", async (req, res) => {
  const { clientId } = req.params;
  try {
    const messages = await pool.query("SELECT * FROM messages WHERE client_id = $1 ORDER BY sent_at DESC", [clientId]);
    res.json(messages.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Create a new message
router.post("/", async (req, res) => {
  const { client_id, content, channel, direction } = req.body;
  try {
    const newMessage = await pool.query(
      "INSERT INTO messages (client_id, content, channel, direction) VALUES ($1, $2, $3, $4) RETURNING *",
      [client_id, content, channel, direction]
    );
    res.status(201).json(newMessage.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Update a message
router.put("/:id", async (req, res) => {
  const { id } = req.params;
  const { content, channel, direction } = req.body;
  try {
    const updatedMessage = await pool.query(
      "UPDATE messages SET content = $1, channel = $2, direction = $3 WHERE id = $4 RETURNING *",
      [content, channel, direction, id]
    );
    if (updatedMessage.rows.length === 0) {
      return res.status(404).json({ error: "Message not found" });
    }
    res.json(updatedMessage.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Delete a message
router.delete("/:id", async (req, res) => {
  const { id } = req.params;
  try {
    const deleted = await pool.query("DELETE FROM messages WHERE id = $1 RETURNING *", [id]);
    if (deleted.rows.length === 0) {
      return res.status(404).json({ error: "Message not found" });
    }
    res.json({ message: "Message deleted" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
