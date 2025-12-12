const express = require('express');
const { MongoClient } = require('mongodb');
const app = express();
const PORT = 3000;

app.use(express.json());

// CORS
app.use(function (req, res, next) {
    res.header('Access-Control-Allow-Origin', '*');
    res.header(
        'Access-Control-Allow-Methods',
        'GET,PUT,POST,PATCH,DELETE,OPTIONS'
    );
    res.header(
        'Access-Control-Allow-Headers',
        'Content-Type, Authorization, Content-Length, X-Requested-With'
    );
    if (req.method === 'OPTIONS') res.sendStatus(200);
    else next();
});

// MongoDB Atlas connection string
const uri = 'mongodb+srv://oaa54cs3398:Password123@cluster0.tsiio.mongodb.net/?appName=Cluster0'; // From SWE class, we created this with MongoDB --> https://fibersync-fd2e2.web.app/
const client = new MongoClient(uri);

async function startServer() {
    try {
        await client.connect();
        const db = client.db('library_db');
        const books = db.collection('books');

        // GET /books
        // return list of title and id of all books
        app.get('/books', async (req, res) => {
            try {
                const { avail } = req.query;
                const filter = {};
                if (typeof avail !== 'undefined') {
                    filter.avail = avail === 'true';
                }
                const cursor = books.find(filter, { projection: { _id: 0, id: 1, title: 1 } });
                const arr = await cursor.toArray();
                res.json(arr.map(b => ({ id: b.id, title: b.title })));
            } catch (err) {
                console.error(err);
                res.sendStatus(500);
            }
        });

        // GET /books/:id
        app.get('/books/:id', async (req, res) => {
            try {
                const { id } = req.params;
                const book = await books.findOne({ id });
                if (!book) return res.sendStatus(404);
                res.status(200).json(book);
            } catch (err) {
                console.error(err);
                res.sendStatus(500);
            }
        });

        // POST /books
        app.post('/books', async (req, res) => {
            try {
                const newBook = req.body;
                if (!newBook || typeof newBook.id === 'undefined') {
                    return res.status(400).json({ error: 'id is required' });
                }
                const existing = await books.findOne({ id: String(newBook.id) });
                if (existing) {
                    return res.status(403).json({ error: 'Book with this id already exists' });
                }

                const toInsert = {
                    id: String(newBook.id),
                    title: newBook.title || '',
                    author: newBook.author || '',
                    publisher: newBook.publisher || '',
                    isbn: newBook.isbn || '',
                    avail: typeof newBook.avail === 'boolean' ? newBook.avail : true,
                    who: newBook.who || '',
                    due: newBook.due || ''
                };

                await books.insertOne(toInsert);
                res.status(201).json(toInsert);
            } catch (err) {
                console.error(err);
                res.sendStatus(500);
            }
        });

        // PUT /books/:id
        app.put('/books/:id', async (req, res) => {
            try {
                const { id } = req.params;
                const updates = { ...req.body };
                if (Object.prototype.hasOwnProperty.call(updates, 'id')) {
                    delete updates.id;
                }

                const result = await books.findOneAndUpdate(
                    { id },
                    { $set: updates },
                    { returnDocument: 'after', projection: { _id: 0 } }
                );

                if (!result.value) return res.sendStatus(404);
                res.status(200).json(result.value);
            } catch (err) {
                console.error(err);
                res.sendStatus(500);
            }
        });

        // DELETE /books/:id
        app.delete('/books/:id', async (req, res) => {
            try {
                const { id } = req.params;
                const result = await books.findOneAndDelete({ id });
                if (!result.value) return res.sendStatus(204);
                res.status(200).json(result.value);
            } catch (err) {
                console.error(err);
                res.sendStatus(500);
            }
        });

        // Start server on http://localhost:3000
        app.listen(PORT, () => {
            console.log(`Library server listening at http://localhost:${PORT}`);
        });

        // Graceful shutdown
        process.on('SIGINT', async () => {
            console.log('Shutting down...');
            await client.close();
            process.exit(0);
        });
    } catch (err) {
        console.error('Failed to connect to MongoDB', err);
        process.exit(1);
    }
}

startServer();
