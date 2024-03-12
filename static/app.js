const mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/mydatabase');
const bcrypt = require('bcrypt');
const userSchema = new mongoose.Schema({
    username: String,
    password: String,
});
userSchema.methods.isValidPassword = function(password) {
    return bcrypt.compareSync(password, this.password);
};
const User = mongoose.model('User', userSchema);
const express = require('express');
const app = express();
app.use(express.json());

app.post('/signup', (req, res) => {
    const hashedPassword = bcrypt.hashSync(req.body.password, 10);
    const user = new User({ username: req.body.username, password: hashedPassword });
    user.save((err) => {
        if (err) return res.status(500).send(err);
        res.status(200).send('User created');
    });
});

app.post('/login', (req, res) => {
    User.findOne({ username: req.body.username }, (err, user) => {
        if (err) return res.status(500).send(err);
        if (!user || !user.isValidPassword(req.body.password)) return res.status(401).send('Invalid credentials');
        res.status(200).send('Logged in');
    });
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});