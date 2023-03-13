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
    window.FB.getLoginStatus((response) => {
      console.log(response.authResponse?.accessToken);
      setFacebookUserAccessToken(response.authResponse?.accessToken);
      return response.status;
    });
  };

  function logInToFB () {
    window.FB.login(
      (response) => {
        setFacebookUserAccessToken(response.authResponse?.accessToken);
      },
      {
        // Scopes that allow us to publish content to Instagram
        scope: "instagram_basic,pages_show_list",
      }
    );
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
          resolve(response.instagram_business_account.id);
        }
      );
    });
  };

  const createMediaObjectContainer = (instagramAccountId) => {
    return new Promise((resolve) => {
      window.FB.api(
        `${instagramAccountId}/media`,
        "POST",
        {
          access_token: facebookUserAccessToken,
          image_url: imageUrl,
          caption: postCaption,
        },
        (response) => {
          resolve(response.id);
        }
      );
    });
  };

  const publishMediaObjectContainer = (
    instagramAccountId,
    mediaObjectContainerId
  ) => {
    return new Promise((resolve) => {
      window.FB.api(
        `${instagramAccountId}/media_publish`,
        "POST",
        {
          access_token: facebookUserAccessToken,
          creation_id: mediaObjectContainerId,
        },
        (response) => {
          resolve(response.id);
        }
      );
    });
  };

  async function shareInstagramPost(imageUrl, postCaption) {
    setImageUrl(imageUrl);
    setPostCaption(postCaption);
    console.log(imageUrl);
    console.log(postCaption);
    const facebookPages = await getFacebookPages();
    console.log(facebookPages[0].id);
    const instagramAccountId = await getInstagramAccountId(facebookPages[0].id);
    console.log(instagramAccountId);
    const mediaObjectContainerId = await createMediaObjectContainer(
      instagramAccountId
    );

    await publishMediaObjectContainer(
      instagramAccountId,
      mediaObjectContainerId
    );

    // Reset the form state
    setImageUrl("");
    setPostCaption("");
  };

  return {
    logInToFB,
    shareInstagramPost
  };
}

export default Facebook;