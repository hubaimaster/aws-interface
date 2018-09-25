# Function Definition
### Describe the request and response format of the API defined in the controller.protocol.API

# Each function is defined in the following format

## Function Name
> Description of the function
#### Request
>The parameter of each function is one request object that inherits the dictionary data type.

#### Response
>Each function returns a response object that inherits the dictionary data type.

# Functions 1.0

## create_backend_service
> Create backend service
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        
    },
}
```


## get_backend_service_list
> Get list of backend service item
#### Request
```javascript
{
    passport: dict,
    params: {
        
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        items: [
            {
                id: string,
                name: string,
                member_enabled: Bool,
                model_enabled: Bool,
            }, ...
        ]
    },
}
```


## get_backend_service
> Get backend service 
#### Request
```javascript
{
    passport: dict,
    params: {
        name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        item: {
            id: string,
            name: string,
            member_enabled: bool,
            model_enabled: bool,
        }
    },
}
```



## set_user_table_enabled
> Set member function enabled 
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
        enabled: bool,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        
    },
}
```




## create_user_table
> Create user table (Private) 
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        
    },
}
```



## create_user_property
> Create user table property
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
        name: string,
        data_type: string,
        read_group_name: string,
        write_group_name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        
    },
}
```



## create_user_group
> Create user permission group
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
        name: string,
        desc: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        
    },
}
```


## create_user
> Create user 
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        item: {
            id: string,
            creationDate: int,
        }
    },
}
```


## delete_user
> Delete user by user_id
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
        id: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        
    },
}
```



## delete_user_group
> Delete user group by group_name
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
        name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        
    },
}
```



## get_user_group_list
> Get list of user group
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        items: [
            {
                name: string,
                desc: string,
            }
        ]
    },
}
```



## get_user_property_list
> Get list of user model property
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        items: [
            {
                name: string,
                dataType: string,
                required: bool,
                read_group_name: string,
                write_grouo_name: string,
            }
        ]
    },
}
```



## get_user_list
> Get list of user
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
        reversed: bool,
        limit: int,
        page: int,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        items: [
            {
                id: string,
                creationDate: string,
                ...
            },
        ]
    },
}
```



## create_model_table
> Create model table such as post, comment, ...
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
        name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        
    },
}
```



## create_model
> Create model item
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
        model_table_name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        item: {
            id: string,
            creationDate: int,
        }
    },
}
```



## get_model_property_list
> Get list of model table property
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
        model_table_name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        items: [
            {
                name: string,
                dataType: string,
                read_group_name: string,
                write_grouo_name: string,
            }
        ]
    },
}
```



## get_model_table_list
> Get list of model table
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        items: [
            {
                name: string,
            }
        ]
    },
}
```



## get_model_list
> Get list of model item
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
        model_table_name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
        items: [
            {
                id: string,
                creationDate: int,
                ...
            }, ..
        ]
    },
}
```


## delete_model
> Delete model item by id
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
        id: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
    
    },
}
```


## delete_model_table
> Delete model table by model table name
#### Request
```javascript
{
    passport: dict,
    params: {
        service_name: string,
        name: string,
    },
}
```

#### Response
```javascript
{
    message: {
        code: string, 
        text: string,
    }, data: {
    
    },
}
```
