{% macro to_inr(amount_col, currency_col) %}
    case {{ currency_col }}
        when 'INR' then {{ amount_col }} * 1.00
        when 'USD' then {{ amount_col }} * 87.25
        when 'EUR' then {{ amount_col }} * 94.60
        when 'GBP' then {{ amount_col }} * 111.30
        when 'JPY' then {{ amount_col }} * 0.58
        else null
    end
{% endmacro %}