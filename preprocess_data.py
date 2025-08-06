import pandas as pd
import json
import chess
import os
import urllib.request
import zipfile

OPENINGS_FILE = 'openings.json'
CSV_URL = 'https://storage.googleapis.com/kaggle-datasets/342808/742694/chess_games.csv.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=web%40kaggle-161607.iam.gserviceaccount.com%2F20240510%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20240510T000000Z&X-Goog-Expires=345600&X-Goog-SignedHeaders=host&X-Goog-Signature=abc123def456...'  # ← REPLACE THIS

DATA_DIR = 'data'
CSV_PATH = os.path.join(DATA_DIR, 'chess_games.csv')
ZIP_PATH = os.path.join(DATA_DIR, 'chess_games.csv.zip')

def download_dataset():
    if os.path.exists(CSV_PATH):
        print("✅ Dataset already exists.")
        return

    print("📥 Downloading chess dataset...")
    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        urllib.request.urlretrieve(CSV_URL, ZIP_PATH)
        print("✅ Downloaded zip")

        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)
        print("✅ Extracted dataset")

        os.remove(ZIP_PATH)
    except Exception as e:
        print("❌ Failed to download:", e)
        print("👉 Manually download from Kaggle and put in /data")
        exit(1)

def load_and_process_openings():
    if not os.path.exists(CSV_PATH):
        print("❌ CSV not found! Did you download it?")
        exit(1)

    print("🧠 Building opening book from 200k+ games...")
    df = pd.read_csv(CSV_PATH)
    df = df[(df['white_rating'] >= 2000) & (df['black_rating'] >= 2000)]
    df = df.head(50000)  # Speed up

    opening_book = {}

    for _, row in df.iterrows():
        moves = str(row['moves']).strip().split()
        board = chess.Board()
        for i in range(min(15, len(moves) - 1)):
            try:
                board.push_san(moves[i])
                fen_key = board.fen().split(' ')[0]
                turn = board.turn
                next_move = moves[i+1]
                key = f"{fen_key}_{turn}"
                if key not in opening_book:
                    opening_book[key] = {}
                opening_book[key][next_move] = opening_book[key].get(next_move, 0) + 1
            except:
                break

    with open(OPENINGS_FILE, 'w') as f:
        json.dump(opening_book, f)
    print(f"✅ Opening book saved: {OPENINGS_FILE}")

if __name__ == '__main__':
    download_dataset()
    load_and_process_openings()
