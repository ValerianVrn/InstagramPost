import { useContext, useState } from 'react';
import { useRouter } from 'next/router';
import { AuthContext } from './components/AuthContext';

const USERNAME = 'gourmet';
const PASSWORD = 'gpt';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();
  const { setIsAuthenticated } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // GitHub Pages does not authorized server-side programs.
    // // Send login data to server for validation
    // const response = await fetch('/api/login', {
    //   method: 'POST',
    //   body: JSON.stringify({ username, password }),
    //   headers: {
    //     'Content-Type': 'application/json'
    //   }
    // });

    // if (response.ok) {
    //   // User is authenticated, redirect to protected page
    //   setIsAuthenticated(true);
    //   router.push('/');
    // } else {
    //   // Authentication failed, display error message
    //   alert('Invalid username or password');
    // }

    // Verify the username and password against a database or other source of authorized users
    if (username === USERNAME && password === PASSWORD) {
      // User is authenticated, redirect to protected page
      setIsAuthenticated(true);
      router.push('/');
    } else {
      // Authentication failed, display error message
      alert('Invalid username or password');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit">Login</button>
    </form>
  );
}

export default LoginPage;
