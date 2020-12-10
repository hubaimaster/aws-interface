---
title: SDK API Reference

language_tabs: 
  - shell
  - python
  - javascript
  - java
  - swift


toc_footers:
- <a href='https://aws-interface.com'>AWS Interface</a>

includes:
  - errors

search: true
---
# Introduction

AWS-Interface lets you jump start your next big idea with a powerful and flexible backend. Amazon's web services were meant to be easy and simple—but they're simply not ☹️. There are often too many services for us mere mortals to track. With AWS Interface, we take away the nitty-gritty and let you focus on your ideas and your business.

Here's how it works: register your AWS IAM credentials for us to work with. Then, select the Service that you need for your backend service and tweak them through our website. That's it! We've built an infinitely scalable backend for your service via AWS services, and an auto-generated SDK for the frontend platform of your choice.

[Dashboard console](https://console.aws-interface.com)

# Quickstart
## Set AWS IAM AccessKey permissions
To use AWSI, you need to create a user with administrator rights in AWS IAM to obtain Access Key and SecretKey. AWS Account Creation and [Shortcut](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/) Issuance of Key after IAM User Creation [Shortcut](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html)
Please refer to the shortcut. If you created an IAM user and received an Access Key and Secret Key, use IAM
You must grant the administrator authority to the person. In the AWS IAM console, select the user entry and add the
When you click it, you will see the following screen.

<img src="images/aws_ak/1.png"><br>

Click the Add Permission button in the above state, and then enter AdministratorAccess in the search box in the existing policy direct connection tab.
And check the AdministratorAccess entry to make it look like this:

<img src="images/aws_ak/2.png"><br>

Next: Click the Review button and click the Add Permissions button to grant AdministratorAccess permissions.

<img src="images/aws_ak/3.png"><br>

Again, on the Users> Permissions tab, verify that the AdministratorAccess permissions were successfully granted, and then click the Security Eligibility tab.
Go to the Create Access Keys button.

<img src="images/aws_ak/4.png"><br>


After that, the access key is automatically generated as shown below. At this time, click the Download .csv file button to save the key.

<img src="images/aws_ak/5.png"><br>

Now open the saved accessKeys.csv file and enter AccessKey and SecretKey at AWSI membership. You are now ready to use all the features of AWSI.
## Download SDK

> Create and prepare the SDK Client as follows

```shell
Install CURL (https://curl.haxx.se/)
```

```python
import aws_interface
client = aws_interface.Client()
```

```javascript
// Running in chrome
<script src="aws_interface.js"></script>
<script>
      const client = new Client();
</script>

// Running in node.js
const aws_interface = require('./aws_interface.js');
const client = new aws_interface.Client();
```


```java
AWSInterface client = new AWSInterface();
```

```swift
let client = AWSI()
```
At console.aws-interface.com/apps, click the Create New Backend button to create the backend with the desired name.
After about 3 minutes of AWS resource creation, download the SDK in the desired language.

<img src="images/dashboard/sdk.png"><br>

{% for service in services %}
# {{service.name}}
{{service.description}}
{% for function in service.functions %}
## {{function.name}}

> The question mark after the parameter means that the parameter is not required

```shell
curl "https://your_rest_api_url" -d '{
"module_name": "{{function.name}}"{% for key in function.input_format %},
"{{key}}": {{function.input_format[key]|tojson}}{% endfor %}}'
```

```python
response = client.call_api("{{function.name}}", {{function.input_format|tojson(True)}})
print(response)
```

```javascript
client.callAPI("{{function.name}}", {{function.input_format|tojson(True)}}).then(function(response){
  console.log(JSON.stringify(response));
}).catch(function(error){
    console.log(error.error);
});
```


```java
HashMap<String, Object> data = new HashMap<>();
{% for key in function.input_format %}data.put("{{key}}", {{function.input_format[key]|tojson}});
{% endfor %}
client.callAPI("{{function.name}}", data, (response, hasError)->{
  System.out.println(response);
});
```

```swift
client.callAPI(module_name: "cloud.auth.guest", data: [
{% for key in function.input_format %}"{{key}}": {{function.input_format[key]|tojson}},
{% endfor %}]) { (response) in
  print(response)
}
```

> Expect output:

```json
{{function.output_format|tojson(True)}}
```

{{function.description}}

### HTTP Request

`POST https://you_rest_api_url/`

### Parameters
 
Parameter | Type | Value
--------- | ----------- | -----
module_name | str | "{{function.name}}"
{% for key in function.input_format %}{{key}} | {{function.input_format[key]}}
{% endfor %}

{% endfor %}
{% endfor %}

