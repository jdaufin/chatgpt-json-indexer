import json
import argparse
from pathlib import Path

def load_conversations(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("conversations", data)  # fallback if structure is flat

def list_conversations(conversations):
    for idx, convo in enumerate(conversations):
        title = convo.get("title", "Untitled")
        created = convo.get("create_time", "Unknown")
        print(f"[{idx}] {title} ({created})")

def export_conversation(conversations, index, output_path):
    convo = conversations[index]
    messages = convo.get("mapping", convo.get("messages", []))
    if isinstance(messages, dict):
        messages = [node for node in messages.values() if "message" in node and node["message"]]

    with open(output_path, 'w', encoding='utf-8') as out:
        for msg in messages:
            role = msg.get("message", {}).get("author", {}).get("role", "unknown")
            content = msg.get("message", {}).get("content", {}).get("parts", [""])
            out.write(f"{role.upper()}:\n")
            out.write(content[0] + "\n\n")
    print(f"Conversation saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="ChatGPT JSON Archive Tool")
    parser.add_argument("json_path", help="Path to the exported JSON file")
    parser.add_argument("--list", action="store_true", help="List all conversations")
    parser.add_argument("--export", type=int, help="Export conversation at given index")
    parser.add_argument("--output", type=str, default="conversation.md", help="Output file path")

    args = parser.parse_args()
    conversations = load_conversations(args.json_path)

    if args.list:
        list_conversations(conversations)
    elif args.export is not None:
        export_conversation(conversations, args.export, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()