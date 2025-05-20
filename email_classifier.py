

class EmailClassifier:
    
    def __init__(self, llm):
        self.llm = llm
       # self.prompt = self.prompt

    def classify_email(self, email_text, sender_email, email_subject):
        prompt =f"""
        You are a helpful personal assistant who shileds me from distraction, spam, marketing, and other unwanted emails.
        I am more interested in knowing whether an email is related to any job opportunity, or bill payment.
        If the email is from recruiter or job portal or has any job-related keywords, classify it as "job".
        If the email is about a bill payment remainder or contains potential invoice, classify as "bill".
        Everything else you can generelally classify into one of the thre "marketing", "advertisement", or "noise".
        You are not allowed to classify any email as "work" or "job" unless it is explicitly related to job opportunity.
        You are not allowed to classify any email as "bill" unless it is explicitly related to bill payment.
        Classify the following email into one of these categories: **work, job, bill, noise**.  
        Use both the email content AND the sender/recipient information to determine the most appropriate label.

        ### Email Metadata:
        - **From**: {sender_email}
        - **Subject**: {email_subject}

        ### Email Body:
        {email_text}

        ### Instructions:
        1. Analyze the sender/recipient addresses (e.g., emails from "@invoices.com" are likely bills).  
        2. Check for keywords in the subject/body (e.g., "meeting" → work, "recruitment" → job).  
        3. If the email is clearly unsolicited (e.g., "@marketing.com"), classify as "noise".  
        4. Provide your reasoning before assigning the label.

        ### Output Format:
        **Reasoning**: <Explain your logic here>  
        **Label**: <work/job/bill/noise>
        """
        response = self.llm.invoke(prompt)
            # Extract content from AIMessage object
        response_text = response.content
        print(f"Response: {response_text}")
        # Handle different response formats
        if "Label:" in response_text:
            return response_text.split("Label: ")[-1].strip().lower()
        elif "**Label**:" in response_text:  # Handle markdown variants
            return response_text.split("**Label**:")[-1].strip().lower()
        else:
            # Fallback: Take the last word as label
            return response_text.strip().split()[-1].lower()
    # Extract label from response (e.g., split on "Label: ")
        
    
# Example usage     
if __name__ == "__main__":
    from langchain_mistralai import ChatMistralAI
    llm = ChatMistralAI(model="mistral:7b-instruct", temperature=0.0, endpoint="http://localhost:11434/v1")
    
    email_classifier = EmailClassifier(llm)
    
    # Example email data
    email_text = "Hello, I would like to schedule a meeting for next week."
    sender_email = "sales@discount.com"
    email_subject = "Meeting Request"
    label = email_classifier.classify_email(email_text, sender_email, email_subject)   
    print(f"Classified label: {label}")
