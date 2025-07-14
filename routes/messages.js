const express = require('express');
const router = express.Router();
const pool = require('../db');

// GET: Tüm mesajları getir
router.get('/', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM messages ORDER BY created_at DESC');
    res.json(result.rows);
  } catch (err) {
    console.error('Error fetching messages:', err);
    res.status(500).json({ error: 'Could not fetch messages' });
  }
});

// POST: Yeni mesaj ekle
router.post('/', async (req, res) => {
  const { client_id, direction, message } = req.body;
  try {
    const result = await pool.query(
      'INSERT INTO messages (client_id, direction, message) VALUES ($1, $2, $3) RETURNING *',
      [client_id, direction, message]
    );
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error inserting message:', err);
    res.status(500).json({ error: 'Could not add message' });
  }
});

module.exports = router;

// POST: WhatsApp'tan gelen mesajları kaydet (webhook)
router.post('/webhook', async (req, res) => {
  try {
    const body = req.body;

    // WhatsApp payload yapısına göre client_id belirlenmeli
    const phone = body?.entry?.[0]?.changes?.[0]?.value?.messages?.[0]?.from;
    const messageText = body?.entry?.[0]?.changes?.[0]?.value?.messages?.[0]?.text?.body;

    // Veritabanında bu numaraya ait müşteri var mı kontrol et
    const clientCheck = await pool.query('SELECT id FROM clients WHERE phone = $1', [phone]);

    if (clientCheck.rows.length === 0) {
      console.warn("Yeni müşteri: ", phone);
      return res.status(200).json({ status: 'client not found' });
    }

    const client_id = clientCheck.rows[0].id;

    // Mesajı ekle
    await pool.query(
      'INSERT INTO messages (client_id, direction, message) VALUES ($1, $2, $3)',
      [client_id, 'in', messageText]
    );

    res.status(200).json({ status: 'message saved' });

  } catch (err) {
    console.error('Webhook error:', err);
    res.status(500).json({ error: 'Webhook failed' });
  }
});
