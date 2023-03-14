import React, { useEffect, useState } from "react";

export function Facebook() {
  const [imageUrl, setImageUrl] = useState("");
  const [postCaption, setPostCaption] = useState("");
  const [facebookUserAccessToken, setFacebookUserAccessToken] = useState("");
  
  useEffect(() => {
    getLoginStatus();
   }, []);
   
  /* --------------------------------------------------------
   *                      FACEBOOK LOGIN
   * --------------------------------------------------------
   */
  const getLoginStatus = () => {
    console.log("getLoginStatus");
    window.FB.getLoginStatus((response) => {
      console.log(response.authResponse?.accessToken);
      setFacebookUserAccessToken(response.authResponse?.accessToken);
      return response.status;
    });
    console.log("getLoginStatus - done");
  };

  const logInToFB = () => {
    console.log("logInToFB");
    window.FB.login(
      (response) => {
        console.log(response.authResponse?.accessToken);
        setFacebookUserAccessToken(response.authResponse?.accessToken);
      },
      {
        // Scopes that allow us to publish content to Instagram
        scope: "instagram_basic,instagram_content_publish,pages_show_list",
      }
    );
    console.log("logInToFB - done");
  };

  const logOutOfFB = () => {
    window.FB.logout(() => {
      setFacebookUserAccessToken(undefined);
    });
  };

  /* --------------------------------------------------------
   *             INSTAGRAM AND FACEBOOK GRAPH APIs
   * --------------------------------------------------------
   */

  const getFacebookPages = () => {
    return new Promise((resolve) => {
      window.FB.api(
        "me/accounts",
        { access_token: facebookUserAccessToken },
        (response) => {
          console.log(response);
          resolve(response.data);
        }
      );
    });
  };

  const getInstagramAccountId = (facebookPageId) => {
    return new Promise((resolve) => {
      window.FB.api(
        facebookPageId,
        {
          access_token: facebookUserAccessToken,
          fields: "instagram_business_account",
        },
        (response) => {
          console.log(response);
          resolve(response.instagram_business_account.id);
        }
      );
    });
  };

  const createMediaObjectContainer = (instagramAccountId, url, caption) => {
    return new Promise((resolve) => {
      console.log("createMediaObjectContainer");
      console.log("POST " + `${instagramAccountId}/media` + `?access_token=${facebookUserAccessToken}&image_url=${url}&caption=${caption}`);
      window.FB.api(
        `${instagramAccountId}/media`,
        "POST",
        {
          access_token: facebookUserAccessToken,
          image_url: url,
          caption: caption,
        },
        (response) => {
          console.log(response);
          resolve(response.id);
        }
      );
      console.log("createMediaObjectContainer - done");
    });
  };

  const publishMediaObjectContainer = (
    instagramAccountId,
    mediaObjectContainerId
  ) => {
    return new Promise((resolve) => {
      console.log("publishMediaObjectContainer");
      window.FB.api(
        `${instagramAccountId}/media_publish`,
        "POST",
        {
          access_token: facebookUserAccessToken,
          creation_id: mediaObjectContainerId,
        },
        (response) => {
          console.log(response);
          resolve(response.id);
        }
      );
      console.log("publishMediaObjectContainer - done");
    });
  };

  async function shareInstagramPost(url, caption) {
    const facebookPages = await getFacebookPages();
    console.log('facebookid ' + facebookPages[0].id);
    const instagramAccountId = await getInstagramAccountId(facebookPages[0].id);
    console.log('instagramAccountId ' +instagramAccountId);
    const mediaObjectContainerId = await createMediaObjectContainer(instagramAccountId, url, caption);

    await publishMediaObjectContainer(instagramAccountId, mediaObjectContainerId);

    // Reset the form state
    setImageUrl("");
    setPostCaption("");
  };

  function loginAndPublish(url, caption) {
    console.log("loginAndPublish");
    setImageUrl(url);
    setPostCaption(caption);
    console.log(imageUrl);
    console.log(postCaption);
    FB.getLoginStatus(function(response) {
      if (response.status === 'connected') {
        // The user is logged in and has authenticated your app, so you can proceed with the post publishing
        shareInstagramPost(url, caption);
      }
      else if (response.status === 'not_authorized') {
        // The user is logged in to Facebook, but has not authenticated your app, so you need to ask for permissions
        FB.login(function(response) {
          if (response.authResponse) {
            // The user has granted permissions, so you can proceed with the post publishing
            shareInstagramPost(url, caption);
          } else {
            // The user has not granted permissions, so you cannot proceed with the post publishing
            console.log('User cancelled login or did not fully authorize.');
          }
        }, {scope: 'instagram_basic,instagram_content_publish,pages_show_list'});
      } 
      else {
        // The user is not logged in to Facebook, so you need to ask for login
        FB.login(function(response) {
          if (response.authResponse) {
            // The user has logged in and granted permissions, so you can proceed with the post publishing
            shareInstagramPost(url, caption);
          } else {
            // The user has not logged in, so you cannot proceed with the post publishing
            console.log('User cancelled login or did not fully authorize.');
          }
        }, {scope: 'instagram_basic,instagram_content_publish,pages_show_list'});
      }
    }
  );
  console.log("loginAndPublish - done");
  };

  function publishPost() {
    console.log("publishPost");
    FB.api(
      '/me/media',
      'POST',
      {
        'image_url': imageUrl,
        'caption': postCaption,
        'media_type': 'IMAGE'
      },
      function(response) {
        if (response && !response.error) {
          // Post created successfully
          // Call the function to publish the post on Instagram
          publishOnInstagram(response.id);
        } else {
          console.log('Error creating post: ' + response.error.message);
        }
      }
    );
    console.log("publishPost - done");
  }
  
  function publishOnInstagram(mediaId) {
    console.log("publishOnInstagram");
    FB.api(
      `/${mediaId}`,
      'POST',
      {
        'access_token': facebookUserAccessToken,
        'caption': postCaption,
        'media_type': 'IMAGE',
        'container_module': 'FEED_TIMELINE'
      },
      function(response) {
        if (response && !response.error) {
          console.log('Post published successfully on Instagram!');
        } else {
          console.log('Error publishing post on Instagram: ' + response.error.message);
        }
      }
    );
    
    // Reset the form state
    setImageUrl("");
    setPostCaption("");
    console.log("publishOnInstagram - done");
  };

  return {
    loginAndPublish
  };
}

export default Facebook;