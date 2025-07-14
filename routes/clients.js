const express = require('express');
const router = express.Router();
const pool = require('../db');

// ✅ GET /clients — tüm müşterileri getir
router.get('/', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM clients ORDER BY id DESC');
    res.json(result.rows);
  } catch (err) {
    console.error('❌ Error fetching clients:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ✅ POST /clients — yeni müşteri ekle
router.post('/', async (req, res) => {
  const { name, phone, lastvisit, preferred_employee, notes } = req.body;
  console.log('Incoming client POST:', req.body);

  try {
    const result = await pool.query(
      'INSERT INTO clients (name, phone, lastvisit, preferred_employee, notes) VALUES ($1, $2, $3, $4, $5) RETURNING *',
      [name, phone, lastvisit, preferred_employee, notes]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('❌ Error inserting client:', err);
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
