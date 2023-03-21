import React, { useEffect, useState } from 'react'
import App from 'next/app'
import AuthProvider from './components/AuthContext';
import 'bootstrap/dist/css/bootstrap.css'

export default function MyApp({ Component, pageProps }) {
  const [sdkInitialized, setSdkInitialized] = useState(false);

  useEffect(() => {

    // Initialize Facebook SDK.
    window.fbAsyncInit = () => {
      FB.init({
        // appId: process.env.OPENAI_API_KEY,

            appId: '596915082341166',
            cookie: true,
            xfbml: true,
            version: 'v16.0'
          });
    
          // Set the initialization status to true
          setSdkInitialized(true);
        };
    
        // Load the Facebook SDK asynchronously
        (function(d, s, id) {
          var js, fjs = d.getElementsByTagName(s)[0];
          if (d.getElementById(id)) return;
          js = d.createElement(s); js.id = id;
          js.src = "https://connect.facebook.net/en_US/sdk.js";
          fjs.parentNode.insertBefore(js, fjs);
        }(document, 'script', 'facebook-jssdk'));
      }, []);

        if (!sdkInitialized) {
          return <div>Loading...</div>;
        }
    
        return (
        <AuthProvider>
          <Component {...pageProps} />
        </AuthProvider>
        );
}
