
import discord
from discord.ext import commands
import sqlite3
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Set up the Discord bot
intents = discord.Intents.default()
intents.message_content = True  # Enable receiving message content
bot = commands.Bot(command_prefix='!', intents=intents)

# Connect to the SQLite database
conn = sqlite3.connect('chatbot.db')
c = conn.cursor()

# Create a table to store user interactions
c.execute('''CREATE TABLE IF NOT EXISTS interactions
             (user_id INTEGER, query TEXT, response TEXT)''')
conn.commit()

# Load the pre-trained GPT-2 model and tokenizer
model = GPT2LMHeadModel.from_pretrained('ingen51/DialoGPT-medium-GPT4')
tokenizer = GPT2Tokenizer.from_pretrained('ingen51/DialoGPT-medium-GPT4')

# Generate a response based on user input
def generate_response(user_input):
    # Tokenize the user input
    input_ids = tokenizer.encode(user_input, return_tensors='pt')

    # Generate a response using the model
    output = model.generate(input_ids, max_length=100, num_return_sequences=1)
    response = tokenizer.decode(output[0], skip_special_tokens=True)

    return response

# Event handler for message events
@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        user_id = message.author.id
        query = message.content.replace(bot.user.mention, '').strip()

        # Generate a response
        response = generate_response(query)

        # Save the interaction to the database
        c.execute("INSERT INTO interactions VALUES (?, ?, ?)", (user_id, query, response))
        conn.commit()

        # Send the response to the user
        await message.channel.send(response)

    await bot.process_commands(message)

# Run the bot with your bot token
bot.run('your-token-here')
