import ollama
from wand.image import Image


def main():
    image_path = input("Image path: ")
    print('Chat with LLM llava')

    with Image(filename=image_path) as img:
        scale_factor = 300 / img.width
        height = round(img.height * scale_factor)
        img.scale(300, height)
        img.save(filename="/tmp/tmp.jpg")

    response = ollama.chat(
        model='llava',
        options={'temperature': 0.1},
        messages=[{
            'role': 'system',
            'content': 'You are a professional photographer'
        }, {
            'role': 'user',
            'content': '''
                Create a decent amount of hashtags in german and english for a social media post.
                Here is a example:                            
                German:
                #hastag1
                #hastag2               
                ...
                
                English:
                #hastag1
                #hastag2
                ...
             ''',
            'images': ['/tmp/tmp.jpg']
        }]
    )
    print(response.message.content)


if __name__ == '__main__':
    main()