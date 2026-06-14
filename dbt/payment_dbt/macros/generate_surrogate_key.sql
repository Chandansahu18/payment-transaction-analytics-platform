{% macro generate_surrogate_key(fields) %}
    {{ dbt_utils.generate_surrogate_key(fields) }}
{% endmacro %}