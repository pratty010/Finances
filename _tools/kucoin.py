

spot_url = "https://api.kucoin.com"
futures_url = "https://api-futures.kucoin.com"

# User
client = User("66c38017da7a37000120481b", "c7a87b43-8906-4a58-ac23-21fc4ac977b7", "0n3p13c3")


address = client.user_info()

print(address)