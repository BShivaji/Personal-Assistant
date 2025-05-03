from openai import OpenAI
import online 

client = OpenAI(api_key=online.API_KEY)

def send_request(query):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=query + [{"role": "system", "content": "Please provide a concise response, limited to 4 lines."}],
            max_tokens=150,  
            timeout=10  
        )

        response = completion.choices[0].message.content.strip()

        
        lines = response.split("\n")
        trimmed_response = "\n".join(lines[:4])  

        return trimmed_response

    except Exception as e:
        print(f"Error in AI request: {e}")
        return "Sorry, I couldn't process that request."
