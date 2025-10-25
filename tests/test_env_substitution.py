import os

from taskrunner.utils.env_substitution import substitute_env_vars


def test_substitute_env_vars_simple():
    # Set up test environment variable
    os.environ['TEST_VAR'] = 'test_value'
    
    config = {
        'key': '${TEST_VAR}',
        'other_key': 'normal_value'
    }
    
    result = substitute_env_vars(config)
    
    assert result['key'] == 'test_value'
    assert result['other_key'] == 'normal_value'


def test_substitute_env_vars_nested():
    # Set up test environment variable
    os.environ['TEST_VAR'] = 'test_value'
    os.environ['NESTED_VAR'] = 'nested_value'
    
    config = {
        'simple': '${TEST_VAR}',
        'nested_dict': {
            'inner_key': '${NESTED_VAR}',
            'inner_static': 'static_value'
        },
        'list_of_values': [
            '${TEST_VAR}',
            'static_item',
            '${NESTED_VAR}'
        ]
    }
    
    result = substitute_env_vars(config)
    
    assert result['simple'] == 'test_value'
    assert result['nested_dict']['inner_key'] == 'nested_value'
    assert result['nested_dict']['inner_static'] == 'static_value'
    assert result['list_of_values'][0] == 'test_value'
    assert result['list_of_values'][1] == 'static_item'
    assert result['list_of_values'][2] == 'nested_value'


def test_substitute_env_vars_missing_var():
    config = {
        'key': '${NON_EXISTENT_VAR}'
    }
    
    result = substitute_env_vars(config)
    
    # Should remain unchanged if variable doesn't exist
    assert result['key'] == '${NON_EXISTENT_VAR}'


def test_substitute_env_vars_multiple_vars():
    # Set up test environment variables
    os.environ['VAR1'] = 'value1'
    os.environ['VAR2'] = 'value2'
    
    config = {
        'key': 'prefix_${VAR1}_middle_${VAR2}_suffix'
    }
    
    result = substitute_env_vars(config)
    
    assert result['key'] == 'prefix_value1_middle_value2_suffix'


def test_substitute_env_vars_complex_config():
    # Set up test environment variables
    os.environ['HOST'] = 'localhost'
    os.environ['PORT'] = '8080'
    os.environ['API_KEY'] = 'secret123'
    
    config = {
        'database': {
            'host': '${HOST}',
            'port': '${PORT}',
            'credentials': {
                'api_key': '${API_KEY}',
                'timeout': 30
            }
        },
        'services': [
            {
                'name': 'service1',
                'url': 'http://${HOST}:${PORT}/api'
            },
            {
                'name': 'service2',
                'url': 'https://${HOST}/v2'
            }
        ],
        'settings': {
            'debug': True,
            'log_level': 'INFO'
        }
    }
    
    result = substitute_env_vars(config)
    
    assert result['database']['host'] == 'localhost'
    assert result['database']['port'] == '8080'
    assert result['database']['credentials']['api_key'] == 'secret123'
    assert result['database']['credentials']['timeout'] == 30
    assert result['services'][0]['url'] == 'http://localhost:8080/api'
    assert result['services'][1]['url'] == 'https://localhost/v2'
    assert result['settings']['debug'] is True