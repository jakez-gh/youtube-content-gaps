#!/usr/bin/env python3
"""YouTube gap research utilities.

Usage:
  PYTHONPATH=. python scripts/gap_research.py --query "ai prompt engineering" --max-videos 20 --comments 200

Requirements:
  pip install google-api-python-client youtube-transcript-api pandas tqdm
  export YOUTUBE_API_KEY="YOUR_API_KEY"

Outputs:
  data/video_list.csv
  data/comments.csv
  data/transcripts.csv

This script runs real queries against the YouTube Data API, downloads video transcripts, and extracts comments.
"""

import argparse
import csv
import os
import re
import sys
from datetime import datetime

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from tqdm import tqdm

API_KEY_ENV = "YOUTUBE_API_KEY"


def get_youtube_client():
    key = os.environ.get(API_KEY_ENV)
    if not key:
        raise ValueError(f"Set {API_KEY_ENV} environment variable with API key")

    return build("youtube", "v3", developerKey=key)


def search_videos(youtube, query, max_results=20):
    items = []
    request = youtube.search().list(
        part="id,snippet",
        q=query,
        type="video",
        maxResults=min(max_results, 50),
        order="relevance",
        safeSearch="none",
        videoDuration="any",
    )

    response = request.execute()

    items.extend(response.get("items", []))

    # If more than 50 requested, iterate pages
    while len(items) < max_results and "nextPageToken" in response:
        response = youtube.search().list(
            part="id,snippet",
            q=query,
            type="video",
            maxResults=50,
            pageToken=response["nextPageToken"],
            order="relevance",
            safeSearch="none",
            videoDuration="any",
        ).execute()
        items.extend(response.get("items", []))

    return items[:max_results]


def get_video_details(youtube, video_ids):
    if not video_ids:
        return []
    resp = youtube.videos().list(part="snippet,statistics,contentDetails", id=",".join(video_ids), maxResults=len(video_ids)).execute()
    return resp.get("items", [])


def dump_video_list(videos, out_file):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    fields = ["videoId", "title", "description", "publishedAt", "channelTitle", "viewCount", "likeCount", "commentCount", "duration"]
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for v in videos:
            writer.writerow({
                "videoId": v.get("id"),
                "title": v.get("snippet", {}).get("title", ""),
                "description": v.get("snippet", {}).get("description", ""),
                "publishedAt": v.get("snippet", {}).get("publishedAt", ""),
                "channelTitle": v.get("snippet", {}).get("channelTitle", ""),
                "viewCount": v.get("statistics", {}).get("viewCount", ""),
                "likeCount": v.get("statistics", {}).get("likeCount", ""),
                "commentCount": v.get("statistics", {}).get("commentCount", ""),
                "duration": v.get("contentDetails", {}).get("duration", ""),
            })


def normalize_youtube_id(url_or_id):
    # quick heuristic from URL or ID
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        # extract v param or path
        m = re.search(r"v=([A-Za-z0-9_-]{11})", url_or_id)
        if m:
            return m.group(1)
        m = re.search(r"youtu\.be/([A-Za-z0-9_-]{11})", url_or_id)
        if m:
            return m.group(1)
        m = re.search(r"/embed/([A-Za-z0-9_-]{11})", url_or_id)
        if m:
            return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
        return url_or_id
    return None


def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join([seg["text"].strip() for seg in transcript])
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        return None


def dump_transcripts(video_ids, out_file):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["videoId", "transcript"])
        writer.writeheader()
        for vid in tqdm(video_ids, desc="Transcripts"):
            txt = fetch_transcript(vid)
            writer.writerow({"videoId": vid, "transcript": txt or ""})


def fetch_comments(youtube, video_id, max_comments=100):
    comments = []
    request = youtube.commentThreads().list(part="snippet", videoId=video_id, textFormat="plainText", maxResults=100)
    while request and len(comments) < max_comments:
        response = request.execute()
        for item in response.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "videoId": video_id,
                "commentId": top.get("id"),
                "author": top.get("authorDisplayName"),
                "text": top.get("textDisplay"),
                "likeCount": top.get("likeCount"),
                "publishedAt": top.get("publishedAt"),
            })
            if len(comments) >= max_comments:
                break
        request = youtube.commentThreads().list(part="snippet", videoId=video_id, textFormat="plainText", maxResults=100, pageToken=response.get("nextPageToken")) if response.get("nextPageToken") else None
    return comments


def dump_comments(youtube, video_ids, out_file, max_per_video=100):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    fields = ["videoId", "commentId", "author", "text", "likeCount", "publishedAt"]
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for vid in tqdm(video_ids, desc="Comments"):
            rows = fetch_comments(youtube, vid, max_per_video)
            for r in rows:
                writer.writerow(r)


def main():
    parser = argparse.ArgumentParser(description="YouTube gap content research helper")
    parser.add_argument("--query", required=True, help="Search query seed")
    parser.add_argument("--max-videos", type=int, default=20)
    parser.add_argument("--comments", type=int, default=150)
    parser.add_argument("--output-dir", default="data")
    args = parser.parse_args()

    youtube = get_youtube_client()
    results = search_videos(youtube, args.query, args.max_videos)
    video_ids = [item["id"]["videoId"] for item in results if item["id"].get("videoId")]

    details = get_video_details(youtube, video_ids)
    dump_video_list(details, os.path.join(args.output_dir, "video_list.csv"))
    dump_transcripts(video_ids, os.path.join(args.output_dir, "transcripts.csv"))
    dump_comments(youtube, video_ids, os.path.join(args.output_dir, "comments.csv"), max_per_video=args.comments)

    print("Done. Files written to", args.output_dir)


if __name__ == "__main__":
    main()
