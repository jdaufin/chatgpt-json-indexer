import json
import argparse
import curses
from pathlib import Path
import os

def load_conversations(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

def export_conversations(conversations, indices, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)  # Ensure the output directory exists

    for index in indices:
        convo = conversations[index]
        title = convo.get("title", f"conversation_{index}").replace(" ", "_")
        title = "".join(c for c in title if c.isalnum() or c in ('_', '-'))  # Sanitize filename
        filename = output_dir / f"{title}.md"

        write_messages(convo, filename)

def write_messages(convo, output_path):
    """
    Generate Markdown content from the conversation and write it to the output path.
    """
    messages = convo.get("mapping", convo.get("messages", []))
    if isinstance(messages, dict):
        # Flatten and iterate through messages if they are in a dictionary
        messages = [node for node in messages.values() if "message" in node and node["message"]]

    # Extract the title for the document
    title = convo.get("title", "Untitled Conversation")
    title = title.strip()  # Ensure no extra whitespace

    with open(output_path, 'w', encoding='utf-8') as out:
        # Write the conversation title as a Markdown top-level heading
        out.write(f"# {title}\n\n")

        # Iterate over messages to format as Markdown
        for msg in messages:
            # Extract message fields
            role = msg.get("message", {}).get("author", {}).get("role", "unknown").capitalize()
            content = msg.get("message", {}).get("content", {}).get("parts", ["No content"])[0]
            timestamp = msg.get("message", {}).get("create_time", "Unknown timestamp")

            # Write the message in Markdown
            out.write(f"**{role}** ({timestamp}):\n\n")
            
            # If content is a dict or not a string, safely convert it to a string
            if isinstance(content, dict):
                content_str = json.dumps(content, indent=2)  # Convert dict to readable JSON
                out.write(f"`{content_str}`\n\n")
            else:
                out.write(f"{content}\n\n")

            # Separate messages for readability
            out.write("---\n\n")

        print(f"Conversation saved to {output_path}")

def tui_multiselector(conversations):
    selected = {}  # Dictionary to track selected conversation indices

    def draw_menu(stdscr):
        curses.curs_set(0)
        current_row = 0
        offset = 0  # Used to track the current top of the displayed window

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Initialize color pairs: pair number, foreground color, background color
            curses.start_color()
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Highlighted text (selected line)
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Normal text


    # Determine how many lines to display based on terminal height
            max_visible = height - 1  # Reserve 1 line for errors or instructions
            visible_conversations = conversations[offset:offset + max_visible]

            for idx, convo in enumerate(visible_conversations):
                title = convo.get("title", "Untitled")
                created = convo.get("create_time", "Unknown")
                line = f"[{offset + idx}] {title} ({created}) {'[X]' if selected.get(offset + idx) else '[ ]'}"

                if offset + idx == current_row:
                    stdscr.addstr(idx, 0, line[:width], curses.color_pair(1))
                else:
                    stdscr.addstr(idx, 0, line[:width], curses.color_pair(2))

            stdscr.refresh()

            key = stdscr.getch()

            # Navigation logic with terminal constraints
            if key == curses.KEY_UP:
                current_row = max(0, current_row - 1)
                if current_row < offset:
                    offset -= 1
            elif key == curses.KEY_DOWN:
                current_row = min(len(conversations) - 1, current_row + 1)
                if current_row >= offset + max_visible:
                    offset += 1
            elif key == ord(' '):  # Toggle selection with spacebar
                selected[current_row] = not selected.get(current_row, False)
            elif key in [curses.KEY_ENTER, 10, 13]:  # Confirm with Enter
                return [idx for idx, is_selected in selected.items() if is_selected]
            elif key == ord('q'):  # Quit with q
                return []

    return curses.wrapper(draw_menu)

def main():
    parser = argparse.ArgumentParser(description="ChatGPT JSON Archive Tool with TUI")
    parser.add_argument("json_path", help="Path to the exported JSON file")
    parser.add_argument("--tui", action="store_true", help="Enable interactive TUI for selecting conversations")
    parser.add_argument("--output_dir", type=str, default="exports", help="Directory to save exported conversations")

    args = parser.parse_args()
    conversations = load_conversations(args.json_path)

    if args.tui:
        selected_indices = tui_multiselector(conversations)
        export_conversations(conversations, selected_indices, args.output_dir)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()