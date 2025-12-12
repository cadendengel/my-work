const express = require('express');
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

// "Database"
let books = [
    {
        id: '1',
        title: 'Reactions in REACT',
        author: 'Ben Dover',
        publisher: 'Random House',
        isbn: '978-3-16-148410-0',
        avail: true,
        who: '',
        due: ''
    },
    {
        id: '2',
        title: 'Express-sions',
        author: 'Frieda Livery',
        publisher: 'Chaotic House',
        isbn: '978-3-16-148410-2',
        avail: true,
        who: '',
        due: ''
    },
    {
        id: '3',
        title: 'Restful REST',
        author: 'Al Gorithm',
        publisher: 'ACM',
        isbn: '978-3-16-143310-1',
        avail: true,
        who: '',
        due: ''
    },
    {
        id: '4',
        title: 'See Essess',
        author: 'Anna Log',
        publisher: "O'Reilly",
        isbn: '987-6-54-148220-1',
        avail: false,
        who: 'Homer',
        due: '1/1/23'
    },
    {
        id: '5',
        title: 'Scripting in JS',
        author: 'Dee Gital',
        publisher: 'IEEE',
        isbn: '987-6-54-321123-1',
        avail: false,
        who: 'Marge',
        due: '1/2/23'
    },
    {
        id: '6',
        title: 'Be An HTML Hero',
        author: 'Jen Neric',
        publisher: 'Coders-R-Us',
        isbn: '987-6-54-321123-2',
        avail: false,
        who: 'Lisa',
        due: '1/3/23'
    }
];

// GET /books
// return list of title and id of all books
app.get('/books', (req, res) => {
    const { avail } = req.query;

    let result = books;

    // If avail query parameter is present, filter by availability
    if (typeof avail !== 'undefined') {
        const desired = avail === 'true';
        result = books.filter(b => b.avail === desired);
    }

    res.json(result.map(b => ({ id: b.id, title: b.title })));
});

// GET /books/:id
// return all details of a specific book by ID
app.get('/books/:id', (req, res) => {
    const { id } = req.params;
    const book = books.find(b => b.id === id);

    if (!book) {
        return res.sendStatus(404);
    }

    res.status(200).json(book);
});

// POST /books
// Add a new book. Body must contain JSON including id & status.
app.post('/books', (req, res) => {
    const newBook = req.body;

    // Require an id
    if (!newBook || typeof newBook.id === 'undefined') {
        return res.status(400).json({ error: 'id is required' });
    }

    // Check for existing book
    const existing = books.find(b => b.id === newBook.id);
    if (existing) {
        return res.status(403).json({ error: 'Book with this id already exists' });
    }

    books.push({
        id: String(newBook.id),
        title: newBook.title || '',
        author: newBook.author || '',
        publisher: newBook.publisher || '',
        isbn: newBook.isbn || '',
        avail: typeof newBook.avail === 'boolean' ? newBook.avail : true,
        who: newBook.who || '',
        due: newBook.due || ''
    });

    res.status(201).json(newBook);
});

// PUT /books/:id
// Update an existing book by ID
app.put('/books/:id', (req, res) => {
    const { id } = req.params;
    const index = books.findIndex(b => b.id === id);

    if (index === -1) {
        return res.sendStatus(404);
    }

    // Update book details
    const updates = { ...req.body };
    if (Object.prototype.hasOwnProperty.call(updates, 'id')) {
        delete updates.id;
    }

    books[index] = {
        ...books[index],
        ...updates
    };

    res.status(200).json(books[index]);
});

// DELETE /books/:id
// Delete a book by ID
app.delete('/books/:id', (req, res) => {
    const { id } = req.params;
    const index = books.findIndex(b => b.id === id);

    if (index === -1) {
        return res.sendStatus(204);
    }

    const deleted = books.splice(index, 1)[0];
    res.status(200).json(deleted);
});

// Start server on http://localhost:3000
app.listen(PORT, () => {
    console.log(`Library server listening at http://localhost:${PORT}`);
});
