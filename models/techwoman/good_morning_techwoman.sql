{{ config(materialized='view') }}

with source as (
    select
        id,
        title,
        resource_type,
        theme,
        url,
        description,
        source
    from {{ source('public', 'resources_techwoman') }}
    where url is not null
      and length(url) > 10
)

select
    id,
    initcap(title) as title,
    lower(resource_type) as resource_type,
    lower(theme) as theme,
    url,
    description,
    source
from source
