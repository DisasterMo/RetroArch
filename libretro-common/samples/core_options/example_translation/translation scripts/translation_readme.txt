** Introduction **

The scripts that come with this file will aid in converting 'libretro_core_options.h' &
'libretro_core_options_intl.h' to v2 as well as in (re-)creating 'libretro_core_options_intl.h'
using translations from crowdin, once those are available.

** Instructions **

* Preparations & v1 -> v2 conversion *

First, place the scripts into the same folder as 'libretro_core_options.h' & 'libretro_core_options_intl.h'.

None of the scripts can handle code insertion via macros/run-time fill-in, so those need to be manually replaced
with the corresponding code/text snippets, unless there is absolutely no need to translate them 
(usually only true for purely numerical values and some special terms/abbreviations).
The only exception is the option key value:


#define CORE_OPTION_NAME "some_name"
   ...
   {/* it is recommended to replace all macros, but this will still work:
      CORE_OPTION_NAME "option_key",
      
      "Description/Label",
      "Information/Sub-Label",
      {
         { key, value },
         ...
      },
      default,
   }
   ...


While you're at it, might as well check the strings for mistakes/inconsistencies/duplicate entries.
In particular the following should be considered:

 - if the value of a key-value pair is one of the following (regardless of
   capitalization), it's content should be moved to the key & the value should
   be set to NULL instead:
   '"enabled"', '"disabled"', '"true"', '"false"', '"on"', '"off"'


   For example:
   {
      "option_key",
      "Description/Label",
      "Information/Sub-Label",
      {
         { "disabled", NULL }, // perfect
         { "yes",  "enabled" }, // => { "enabled", NULL },
         { NULL, NULL },
      },
      "disabled",
   }


   NOTE: These strings will not be made translatable by this procedure, as they are
         translated by RetroArch itself.


If the core_options files are not already v2, it is recommended to convert them by running 'v1_to_v2_converter.py'.
The old files will be preserved as *.v1 files.

* Translations *

To update 'libretro_core_options_intl.h' when new text has been added to 'libretro_core_options.h' or 
new translations are available from crowdin, run 'translate.py'.

The first time you do, the script will ask for the core name. It is important for the name to be unique to the core.
Has the core name been provided, the script will save it and not ask for it again.
Should there be need to change the core name, the script will need to be modified 
('translate.py', ca. line 36, core_name should be set to an empty string: core_name = '').

The script will then create a <core_name>_us.h file with the texts from 'libretro_core_options.h'.
Converted into a .json, this file will serve as the source for crowdin translations.
If during the creation of the .json duplicate keys are found, the script will notify you about it.
This, however, should never occur.

Next the script will ask whether to sync with crowdin. For a successful sync you'll need a crowdin API key and
sufficient permissions. This will upload the generated '*_us.json' and download all available translations.
The translations will be converted into .h files.

Regardless of your previous choice, the script will then inquire whether to (re-)construct 'libretro_core_options_intl.h'.
Should you decline, the script terminates and all created files will still be there for examination.
If you proceed, the script will overwrite the old 'libretro_core_options_intl.h' with the new translations
after saving a copy of it as 'libretro_core_options_intl.h.v1'.
The created .h translation files will be deleted during this process. The script terminates after this.

After this, add the corresponding entries to 'options_intl' or 'option_defs_intl' in 'libretro_core_options.h'.
Locate libretro.h and ensure 'enum retro_language' is up to date.
As of the time of writing (2021-08-09) it should include:

   RETRO_LANGUAGE_ENGLISH             = 0,
   RETRO_LANGUAGE_JAPANESE            = 1,
   RETRO_LANGUAGE_FRENCH              = 2,
   RETRO_LANGUAGE_SPANISH             = 3,
   RETRO_LANGUAGE_GERMAN              = 4,
   RETRO_LANGUAGE_ITALIAN             = 5,
   RETRO_LANGUAGE_DUTCH               = 6,
   RETRO_LANGUAGE_PORTUGUESE_BRAZIL   = 7,
   RETRO_LANGUAGE_PORTUGUESE_PORTUGAL = 8,
   RETRO_LANGUAGE_RUSSIAN             = 9,
   RETRO_LANGUAGE_KOREAN              = 10,
   RETRO_LANGUAGE_CHINESE_TRADITIONAL = 11,
   RETRO_LANGUAGE_CHINESE_SIMPLIFIED  = 12,
   RETRO_LANGUAGE_ESPERANTO           = 13,
   RETRO_LANGUAGE_POLISH              = 14,
   RETRO_LANGUAGE_VIETNAMESE          = 15,
   RETRO_LANGUAGE_ARABIC              = 16,
   RETRO_LANGUAGE_GREEK               = 17,
   RETRO_LANGUAGE_TURKISH             = 18,
   RETRO_LANGUAGE_SLOVAK              = 19,
   RETRO_LANGUAGE_PERSIAN             = 20,
   RETRO_LANGUAGE_HEBREW              = 21,
   RETRO_LANGUAGE_ASTURIAN            = 22,
   RETRO_LANGUAGE_FINNISH             = 23,


Now compile, add to RetroArch & verify functionality.




