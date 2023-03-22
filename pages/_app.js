import React, { useEffect, useState } from 'react'
import AuthProvider from './components/AuthContext';
import 'bootstrap/dist/css/bootstrap.css'

export default function MyApp({ Component, pageProps }) {

  useEffect(() => {
    // Load the Facebook SDK asynchronously
    (function(d, s, id) {
      var js, fjs = d.getElementsByTagName(s)[0];
      if (d.getElementById(id)) return;
      js = d.createElement(s); js.id = id;
      js.src = "https://connect.facebook.net/en_US/sdk.js";
      fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
  }, []);

  return (
  <AuthProvider>
    <Component {...pageProps} />
  </AuthProvider>
  );
}
