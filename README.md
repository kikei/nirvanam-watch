# nirvanam-watch

[Nirvanam](http://www.nirvanam.jp/) is a South Indian specialty restaurant
in Tokyo, Japan and located near my office.
I'm a just a fan and don't have no connection with them,
but I'm making application to check "today's lunch special menu" automatically.
The menu is published on their [Facebook page](https://www.facebook.com/NirvanamTokyo/).

## Install
At first, you have to get Google Cloud Vision API key from [Google API Console]*https://console.developers.google.com).
Then put it into settings file. If settings file doesn't exist, it can be created from sample file.

    copy settings.py.sample settings.py
    vi settings.py
    GOOGLE_API_KEY = 'YourGoogleAPIKey'
    
