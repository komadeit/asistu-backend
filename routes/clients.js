// clients.js
const express = require("express");
const router = express.Router();
const pool = require("../db");

// Get all clients
router.get("/", async (req, res) => {
  try {
    const allClients = await pool.query("SELECT * FROM clients ORDER BY id DESC");
    res.json(allClients.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get a single client
router.get("/:id", async (req, res) => {
  const { id } = req.params;
  try {
    const client = await pool.query("SELECT * FROM clients WHERE id = $1", [id]);
    if (client.rows.length === 0) {
      return res.status(404).json({ error: "Client not found" });
    }
    res.json(client.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Create a new client
router.post("/", async (req, res) => {
  const { name, phone, lastvisit, preferred_employee, notes } = req.body;
  try {
    const newClient = await pool.query(
      "INSERT INTO clients (name, phone, lastvisit, preferred_employee, notes) VALUES ($1, $2, $3, $4, $5) RETURNING *",
      [name, phone, lastvisit, preferred_employee, notes]
    );
    res.status(201).json(newClient.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Update a client
router.put("/:id", async (req, res) => {
  const { id } = req.params;
  const { name, phone, lastvisit, preferred_employee, notes } = req.body;
  try {
    const updatedClient = await pool.query(
      "UPDATE clients SET name = $1, phone = $2, lastvisit = $3, preferred_employee = $4, notes = $5 WHERE id = $6 RETURNING *",
      [name, phone, lastvisit, preferred_employee, notes, id]
    );
    if (updatedClient.rows.length === 0) {
      return res.status(404).json({ error: "Client not found" });
    }
    res.json(updatedClient.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Delete a client
router.delete("/:id", async (req, res) => {
  const { id } = req.params;
  try {
    const deleted = await pool.query("DELETE FROM clients WHERE id = $1 RETURNING *", [id]);
    if (deleted.rows.length === 0) {
      return res.status(404).json({ error: "Client not found" });
    }
    res.json({ message: "Client deleted" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
