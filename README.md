# Zap2-Serverside

> OBS: This repository should be used in adition to zap2-userside

### Introduction

This project aims to simulate one chat application with end-to-end encryption running through a websocket server. For that it was implemented the Double Ratchet Encryption, if you want to read about it I recommend reading [Niko's post](https://nfil.dev/coding/encryption/python/double-ratchet-example/).

My initial objectives with this project are:
  |                                                                                             |     |
  | --------------------------------------------------------------------------------------------|-----| 
  | Verify provided data, such as checking if the telephone is valid                            | :x: |
  | Implement the Double Ratchet Encryption                                                     | :heavy_check_mark: |
  | Generate new keys for new chatrooms as old keys are used                                    | :x: |
  | Establish the connection between two users through the application                          | :heavy_check_mark: |
  | Implement group chats with encryption                                                       | :x: |
  | Add expiring tokens with something like redis to verify the authenticity of the connection  | :x: |
  | Deal with server connection problems after signup                                           | :x: |
  | Identify and solve problems of data continuity without losing the chat security             | :x: |
  | Implement a half-decent graphical interface                                                 | :white_check_mark: |
  | Make the chat server available on a web domain so it can be tested online                   | :x: |
  | Implement a dockerfile to make it easier to deploy the application                          | :x: |

After this project becomes robust enough I aim to:
  |                                                                                                                         |     |
  | ------------------------------------------------------------------------------------------------------------------------|-----| 
  | Remove the server-side application making it a P2P application                                                          | :x: |
  | Study the possibility of using algorithms for Self-Balancing networks on the P2P web and it's impact on limiting errors | :x: |

### Running the program
To deploy the server you should first install all the requirements executing the following pip command `pip install -r requirements.txt` on the root folder of this repository. After that, assuming you are using one appropriated python version, 3.9.7+, you should traverse to the <i>server</i> folder and run the run.py script with, `python run.py`. After that the server should be running locally.

Then to simulate users using the server you should read the instructions on [this repository](https://github.com/caiocaldeira3/zap2-serverside).





