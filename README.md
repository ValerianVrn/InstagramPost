# Introduction

This is an app for posting AI-generated content on the Instagram account "GourmetPastryTransformer".
Many AI are used to generate caption and images.
A post is published automatically every day.

# How it works

## Daily post

API Graph for Instagram (Meta) (https://developers.facebook.com)
- Facebook Login for Business
Claude API for generating content

### Connect to Instagram

Get access token 
You don't need a login flow at all for a bot. Use the Graph API Explorer to get the token manually just once:

1. Go to developers.facebook.com/tools/explorer
2. Select your app
3. Add permissions: instagram_basic, instagram_content_publish, pages_show_list
4. Click Generate Access Token → log in → copy the token
5. Exchange it for a long-lived token (valid 60 days):

```
bashcurl "https://graph.facebook.com/v19.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id=YOUR_APP_ID
  &client_secret=YOUR_APP_SECRET
  &fb_exchange_token=SHORT_LIVED_TOKEN"
```
6. Paste the result into GitHub Secrets as IG_ACCESS_TOKEN

Since it expires every 60 days, add this to your post.py — it refreshes automatically on every daily run:
```
def refresh_token():
    r = requests.get("https://graph.facebook.com/v19.0/oauth/access_token", params={
        "grant_type":   "ig_refresh_token",
        "access_token": TOKEN,
    })
    if r.ok:
        return r.json().get("access_token")
    return TOKEN
```
Then call it at the top of main and update the state file with the refreshed token — though updating GitHub Secrets programmatically requires an extra setup. Easiest is just to set a reminder every 50 days to refresh it manually via the same curl command.