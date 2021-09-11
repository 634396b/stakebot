pm2 start "python3 main.py" --restart-delay=1000
pm2 start "python3 claim.py" --restart-delay=1000
pm2 start "python3 chat.py" --restart-delay=1000
pm2 start "python3 allHouseBets.py" --restart-delay=1000
# pm2 start "python3 twitter_claim.py" --restart-delay=1000
# pm2 start "python3 stream/live.py" --restart-delay=1000