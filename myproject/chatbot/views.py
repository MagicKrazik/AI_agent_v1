import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
from django.template.loader import render_to_string
import os
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preprocess_html_content():
    try:
        html_content = render_to_string('home.html')
        soup = BeautifulSoup(html_content, 'html.parser')
        
        content = {
            'introduction': soup.find('section', {'id': 'intro'}).get_text(strip=True),
            'features': [li.get_text(strip=True) for li in soup.find('section', {'id': 'features'}).find_all('li')],
            'docker': soup.find('section', {'id': 'docker'}).get_text(strip=True),
            'setup': [li.get_text(strip=True) for li in soup.find('section', {'id': 'setup'}).find_all('li')],
            'image': 'An image illustrating Django and Docker concepts is included in the introduction section.'
        }
        
        return content
    except Exception as e:
        logger.error(f"Error preprocessing HTML content: {str(e)}")
        return {}

home_content = preprocess_html_content()

def create_prompt(user_input):
    prompt = ("Based on the following content about Django and Docker, answer the user's question. "
              "If the question is not related to this content, respond with 'I apologize, but that topic is beyond the scope of the information I have about Django and Docker.'\n\n"
              f"Introduction: {home_content['introduction']}\n\n"
              f"Image: {home_content['image']}\n\n"
              "Key Features of Django:\n" + 
              "\n".join(f"- {feature}" for feature in home_content['features']) + "\n\n"
              f"Docker and Django: {home_content['docker']}\n\n"
              "Setting up Django with Docker:\n" + 
              "\n".join(f"{i+1}. {step}" for i, step in enumerate(home_content['setup'])) + "\n\n"
              f"Human: {user_input}\n\n"
              "Assistant: ")
    return prompt

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('message', '')
            
            if not user_input:
                return JsonResponse({'error': 'No message provided'}, status=400)
            
            prompt = create_prompt(user_input)
            
            # Call Ollama with the prompt
            process = subprocess.Popen(
                ['ollama', 'run', 'llama3.1:8b', prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Error calling Ollama: {stderr}")
                return JsonResponse({'error': f"Error calling Ollama: {stderr}"}, status=500)
            
            response = stdout.strip()
            
            # Remove any error messages from the response
            response = response.replace("failed to get console mode for stdout: The handle is invalid.", "")
            response = response.replace("failed to get console mode for stderr: The handle is invalid.", "")
            
            return JsonResponse({'response': response.strip()})
        
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': f"Unexpected error: {str(e)}"}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)