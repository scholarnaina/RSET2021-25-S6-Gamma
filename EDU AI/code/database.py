import sqlite3

def create_tables(db_file):
  """Creates the 'users', 'user_survey_results', and 'user_results' tables in the given database file."""

  conn = sqlite3.connect(db_file)
  cursor = conn.cursor()
    
  # Create users table with username, name, password (insecure, use hashing!), phone number
  cursor.execute("""
      CREATE TABLE IF NOT EXISTS users (
          username TEXT PRIMARY KEY,
          name TEXT,
          password TEXT UNIQUE,
          phone_number INTEGER,
          UNIQUE(username)
      )
  """)

  
  cursor.execute("""
      CREATE TABLE IF NOT EXISTS user_survey_results (
          username TEXT PRIMARY KEY,
          E INTEGER,  
          I INTEGER,  -- Introversion
          S INTEGER,  -- Sensing
          N INTEGER,  -- Intuition
          T INTEGER,  -- Thinking
          F INTEGER,  -- Feeling
          J INTEGER,  -- Judging
          P INTEGER,  -- Perceiving
          Visual INTEGER,
          Auditory INTEGER,
          Read_Write INTEGER,  -- Combined read/write
          Kinesthetic INTEGER,  -- Removed extra comma
          FOREIGN KEY (username) REFERENCES users(username)
      )
  """)

  cursor.execute("""
      CREATE TABLE IF NOT EXISTS study_materials (
          subject TEXT,
          learning_style TEXT,
          Url TEXT,
          PRIMARY KEY(subject,learning_style)
          )
    """)
        

  # Create user_results table with username (foreign key), prediction, insights
  cursor.execute("""
      CREATE TABLE IF NOT EXISTS user_results (
          username TEXT PRIMARY KEY,
          prediction TEXT,
          insights TEXT,
          UNIQUE(username),
          FOREIGN KEY (username) REFERENCES users(username)
      )
  """)

  conn.commit()
  conn.close()

# Replace "users.db" with your actual database filename
create_tables("users.db")
