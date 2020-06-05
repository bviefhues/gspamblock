# gspamblock
Simple server-side sender-based SPAM blocking for GMail

## Why?
GMail's SPAM filter is broken. I get false positves, legitimate mail classified as SPAM, and that is not really acceptable for a business mail account. On the other hand, I want spam out of my way, automatically, removed from my inbox. This is why I put together gspamblock

## What?
gspamblock is a Google Apps Script, polling your GMail mailbox regularly and checking for mail in eitehr of two folders/with either of two labels. One is for blocking a senders domain, one is for blocking a senders e-mail address. if it finds an email in one of these folders it does the following:

1) Extract the sender email address
2) Create a rule in Gmail, based on the sender email address, for moving any future mail into a spam folder, right on Googles servers, without detour through a local mail client
3) Moving the email it found to the same spam folder

No email gets deleted, all still accessible, with full control over which mail is treated this way

Next to the Google Apps Script, there is a Python script which is useful for maintaining the GMail filter list. The GMail web UI is not really happy with dozens of filter rules (while GMail's backend is fine with this). The Python script shows what the backend sees.
