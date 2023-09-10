# NOTICE

This is a telegram bot that was developed to aid in drafting newsbites for
The LaSallian. While the actual deployed bot is stored in the
[organization's repository](https://github.com/thelasallian/PingBot-OpenSource), this version is the prototype of any
future updates that will be implemented in the bot. 

# How to deploy the bot

1. Install flyctl depending on your machine. You may refer to the [official documentation](https://fly.io/docs/hands-on/install-flyctl/).
2. Login to fly.io `fly auth login` or signup `fly auth signup`.
3. Deploy the application `fly launch`.
4. Expect to answer prompts from the terminal by typing `y` or `n`. Reject setting up a Postgresql database and an Upstash Redis database.

# How to stop the bot

1. Login to the fly.io
2. Navigate to the `application name` in the `dashboard` menu
3. Go to `settings`
4. Choose `Delete app`

# Questions/Concerns?
Reach out to the web section or contact the developer through her telegram `@gleezelluy`

# Technologies used
![Python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=Python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-26A5E4.svg?style=for-the-badge&logo=Telegram&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED.svg?style=for-the-badge&logo=Docker&logoColor=white)
![Fly.io](https://img.shields.io/badge/Fly.io-100000?style=for-the-badge&logo=Fly.io&logoColor=white&labelColor=4B058D&color=470386)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248.svg?style=for-the-badge&logo=MongoDB&logoColor=white)
![PythonAnywhere](https://img.shields.io/badge/PythonAnywhere-1D9FD7.svg?style=for-the-badge&logo=PythonAnywhere&logoColor=white)

