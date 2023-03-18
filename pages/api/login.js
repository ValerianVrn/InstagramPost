import bcrypt from 'bcrypt';

const USERNAME = 'gourmet';
const PASSWORD = 'gpt';

export default async function handler(req, res) {
    
  if (req.method === 'POST') {
    const { username, password } = req.body;
    // Generate a salt to add to the hash
    const salt = await bcrypt.genSalt(10);
    // Hash the password with the salt
    const hash = await bcrypt.hash(PASSWORD, salt);
    // Verify the username and password against a database or other source of authorized users
    if (username === USERNAME && bcrypt.compareSync(password, hash)) {
      // Set a session cookie to indicate that the user is authenticated
      res.status(200).end();
    } else {
      res.status(401).end();
    }
  } else {
    res.status(405).end();
  }
}
