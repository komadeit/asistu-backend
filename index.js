const express = require('express');
const cors = require('cors');
require('dotenv').config();

const clientsRoutes = require('./routes/clients');
const messagesRoutes = require('./routes/messages');

const app = express();
app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.json({ message: 'Asistu backend running!' });
});

app.use('/clients', clientsRoutes);
app.use('/messages', messagesRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

const messagesRouter = require('./routes/messages');
app.use('/messages', messagesRouter);
