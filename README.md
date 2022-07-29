# Exodus :flight_departure:

## About

Migration scripts for converting UTK data to Bulrax CSV import.

## Understanding Configs

Exodus uses `yml` files for migration.  By default, exodus treats everything agnostically and relies on the `xpaths` section
to determine how a concept is mapped.  If a property (or properties) have complex rules, a class can be written
to handle the special case.  When this happens, the `yml` should have a `special` property, and it should be defined in 
`MetadataMapping().__lookup_special_property()`.

An agnostic property should look like this in the `yml`:

```yml
  - name: table_of_contents
    xpaths:
      - 'mods:tableOfContents'
    property: "http://purl.org/dc/terms/tableOfContents"
```

A complex property might look like this:

```yml
  - name: title_and_alternative_title
    xpaths:
      - 'mods:titleInfo[not(@supplied)]/mods:title'
      - 'mods:titleInfo[@supplied="yes"]/mods:title'
    properties:
      - "http://purl.org/dc/terms/title"
      - "http://purl.org/dc/terms/alternative"
    special: "TitleProperty"
```

An agnostic property must always have the `property` property while a complex property may have `property` or `properties`.
