#!/usr/bin/env python3
"""
Scraper for AWS ANS-C01 exam questions from ExamTopics.
Outputs: ans-c01-all.md
"""

import subprocess
import re
import time
import sys

BASE_URL = "https://www.examtopics.com/exams/amazon/aws-certified-advanced-networking-specialty-ans-c01/view/"
TOTAL_PAGES = 55
OUTPUT_FILE = "ans-c01-all.md"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def fetch_page(page_num):
    url = BASE_URL if page_num == 1 else f"{BASE_URL}{page_num}/"
    result = subprocess.run(
        ["curl", "-k", "-s", "-L", "-A", UA, url],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return result.stdout


def strip_tags(html):
    """Remove HTML tags."""
    return re.sub(r'<[^>]+>', '', html)


def decode_entities(text):
    """Decode common HTML entities."""
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#160;', ' ')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&#39;', "'")
    return text


def extract_questions(html):
    """Extract questions from a page's HTML."""
    questions = []

    # Split by question card
    # Each question starts with a div containing question-body
    # We look for the question number markers

    # Find all question blocks
    q_pattern = re.compile(
        r'Question\s+#(\d+).*?Topic\s+(\d+)(.*?)(?=Question\s+#\d+|$)',
        re.DOTALL
    )

    for match in q_pattern.finditer(html):
        q_num = match.group(1)
        topic = match.group(2)
        block = match.group(3)

        # Extract question text - it's in a card-text or question-body element
        # Strip all tags and clean up
        block_text = strip_tags(block)
        block_text = decode_entities(block_text)

        # Normalize whitespace
        lines = [l.strip() for l in block_text.splitlines() if l.strip()]

        # Reconstruct the question content
        # The structure is: question text, then A. B. C. D., then Correct Answer
        full_text = '\n'.join(lines)

        # Extract vote info (most voted answer)
        vote_match = re.search(r'\[\{"voted_answers":\s*"([A-D])".*?"is_most_voted":\s*true', block)
        most_voted = vote_match.group(1) if vote_match else "?"

        # Extract correct answer
        ans_match = re.search(r'Correct Answer[:\s]+([A-D](?:,\s*[A-D])*)', full_text)
        correct_ans = ans_match.group(1) if ans_match else "?"

        # Extract answer choices
        choices = {}
        for letter in ['A', 'B', 'C', 'D']:
            # Match "A." or "A " followed by text up to next choice
            choice_pattern = re.compile(
                rf'{letter}\.\s*(.*?)(?=[B-E]\.|Reveal Solution|Correct Answer|Discussion)',
                re.DOTALL
            )
            cm = choice_pattern.search(full_text)
            if cm:
                choice_text = ' '.join(cm.group(1).split())
                choices[letter] = choice_text

        # Extract question text (before the first answer choice)
        q_text_match = re.search(r'^(.*?)(?:A\.|$)', full_text, re.DOTALL)
        if q_text_match:
            q_text = ' '.join(q_text_match.group(1).split())
            # Remove vote JSON noise if present
            q_text = re.sub(r'\[\{.*?\}\]', '', q_text).strip()
        else:
            q_text = "（題目解析失敗）"

        questions.append({
            'num': q_num,
            'topic': topic,
            'question': q_text,
            'choices': choices,
            'correct': correct_ans,
            'most_voted': most_voted,
        })

    return questions


def format_question(q):
    """Format a question as Markdown."""
    lines = []
    lines.append(f"## Question #{q['num']} (Topic {q['topic']})")
    lines.append("")
    lines.append(q['question'])
    lines.append("")
    for letter in ['A', 'B', 'C', 'D']:
        if letter in q['choices']:
            lines.append(f"- **{letter}.** {q['choices'][letter]}")
    lines.append("")
    lines.append(f"**Correct Answer: {q['correct']}**  ")
    if q['most_voted'] != "?":
        lines.append(f"*Most Voted: {q['most_voted']}*")
    lines.append("")
    lines.append("---")
    lines.append("")
    return '\n'.join(lines)


def main():
    all_questions = []

    for page in range(1, TOTAL_PAGES + 1):
        print(f"Fetching page {page}/{TOTAL_PAGES}...", flush=True)
        html = fetch_page(page)

        if not html or len(html) < 1000:
            print(f"  WARNING: Page {page} returned empty/short content, skipping.")
            continue

        qs = extract_questions(html)
        print(f"  Extracted {len(qs)} questions from page {page}")
        all_questions.extend(qs)

        # Be polite - small delay between requests
        if page < TOTAL_PAGES:
            time.sleep(1.5)

    print(f"\nTotal questions extracted: {len(all_questions)}")

    # Write markdown file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# AWS Certified Advanced Networking - Specialty ANS-C01\n")
        f.write("## Exam Questions (ExamTopics)\n\n")
        f.write(f"- **Total Questions:** {len(all_questions)}\n")
        f.write(f"- **Source:** ExamTopics ANS-C01\n")
        f.write(f"- **Last Updated:** 2026-03-17\n\n")
        f.write("---\n\n")

        for q in all_questions:
            f.write(format_question(q))

    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
