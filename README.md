LostNumber
==========
An anonymous, randomized conversation broker over SMS written in Python using Twilio, Flask and Redis. Think of it as old-school Omegle within your own private network of friends using text messages. 


----------

**Introduction**
========== 
**LostNumber is a generic service which lets you have short, anonymous conversations with members of a private network over text messages.** 

LostNumber is **generic** in the sense that anyone can run LostNumber on a server and establish their own private network. The network is **private** in the sense that in order to join it, *you have to know a specific phone number* (AKA the LostNumber). Once you know the LostNumber, you can join the network and start a conversation with a random member of that private network by sending it text messages.

Here's how it works: 

 - Send two text messages to the LostNumber to register as a member of the network.
 - Start a conversation.
 - The LostNumber forwards messages between yourself and a randomly selected number until a total of 10 messages are exchanged, or one of the participants decides to leave. The forwarded messages include a prefix denoting the U.S. state of the two participants.
 - The conversation ends. 

And that's it. Participants in a conversation can leave at any time, and you can also stop LostNumber from sending you new conversations by going offline.


----------


Why?
----

That's for you to decide. I made it just for fun and practice, but you can (obviously) use it for whatever you like, however it only works in the United States at the moment. 


----------


**Creating Your Own LostNumber Network**
----------

## Prerequisites: ##
Using LostNumber requires that you have access to a [Redis][1] database and a [Twilio][2] account with a phone number. 

To get a Redis database, you can either [install it on your a server][3] using a VPS provider such as [DigitalOcean][4], or access one through a service like [OpenRedis][5] or [Redis Cloud][6]. If you don't already have a Twilio account, sign up at their [website][7], activate it with some money and purchase a phone number. You'll have to deposit at least 20 dollars and a phone number costs $1/month.

## Instructions: ##

 - Clone the LostNumber code. `git clone https://github.com/scascketta/LostNumber.git`
 - Install the requirements, using a [virtualenv][8] is recommended. `pip install -r requirements.txt`
 - In the `app/details.py` file, replace the default values with your Redis address and port, as well as your Twilio Account SID, Auth Token and Twilio phone number. 
 - Start the Flask server. `python run.py` in a [screen][9] session.
 - Start the message dispatch process `python process_msg.py` in another screen session.
 - In your Twilio account, set the Messaging Request URL to your server's public IP address along with port 5000 `:5000`. Make sure the HTTP method is set to `POST`. 
 - Upload `fallback.xml` to anywhere that can publicly serve the file, such as [Amazon S3][10] or [Dropbox][11] and set the Messaging Fallback URL in Twilio to the public link to `fallback.xml`. Make sure the HTTP method is set to `GET`. 

And you're done, try out your new LostNumber by texting your Twilio phone number. 
 

  [1]: http://redis.io/
  [2]: https://www.twilio.com/
  [3]: http://redis.io/download
  [4]: https://www.digitalocean.com/?refcode=2448ebf1fc8a
  [5]: https://openredis.com/
  [6]: http://redis-cloud.com/
  [7]: https://www.twilio.com/
  [8]: http://www.virtualenv.org/en/latest/
  [9]: https://www.gnu.org/software/screen/
  [10]: https://aws.amazon.com/s3/
  [11]: https://www.dropbox.com/help/167/en