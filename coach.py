import os
import google.generativeai as genai

def get_ai_coach_advice(song_data):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Gemini API key not detected. Add GEMINI_API_KEY to environment secrets."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        You are an elite drum instructor. Analyze this track data:
        - Title: {song_data['title']}
        - Artist: {song_data['artist']}
        - Difficulty: {song_data['difficulty']}
        - BPM: {song_data['bpm']}
        - Note Schedule: {song_data['notes']}

        Provide 2 concise, actionable tips to help a drummer master this specific track.
        Keep it direct and encouraging.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error contacting AI Coach: {str(e)}"