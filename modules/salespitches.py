def ld(phenny, input):
    """.longdesc, .ld - long description of Apertium"""
    phenny.say("Apertium is a free/open-source machine translation platform, initially aimed at related-language pairs but expanded to deal with more divergent language pairs (such as English-Catalan).")
    phenny.say("The platform provides:")
    phenny.say("  1. a language-independent machine translation engine")
    phenny.say("  2. tools to manage the linguistic data necessary to build a machine translation system for a given language pair")
    phenny.say("  3. linguistic data for a growing number of language pairs")
    phenny.say("Apertium welcomes new developers: if you think you can improve the engine or the tools, or develop linguistic data for us, do not hesitate to let us know.")
ld.commands = ['ld', 'longdesc']
ld.priority = 'high'
ld.example = '.ld'


def when(phenny, input):
    """.when - when and why to use Apertium"""
    phenny.say("Apertium is a free/open-source machine translation platform.")
    phenny.say("Apertium is not ideal in all situations. It uses rule-based machine translation (RBMT), which is excellent for many, but not all, languages.")
    phenny.say("RBMT gives the best results for closely related languages. Apertium is specifically superior to Google Translate in this scenario, because Google Translate uses English as an intermediate.")
    phenny.say("Another advantage of RBMT is that it works for lesser-resourced languages. Neural machine tranlsation (NMT), used by Google Translate and many other systems, gives excellent results for languages with extremely large bilingual corpora, but breaks down for lesser-resourced languages. RBMT only requires someone who knows both languages and is willing to take the time to create a pair.")
    phenny.say("Overall, Apertium is excellent for closely related languages and for lesser-resourced languages, while NMT or other types of machine tranlsators are often superior for other languages.")
when.commands = ['when']
when.priority = 'high'
when.example = '.when'


def begiak(phenny, input):
    """.about, .info, .begiak - my autobiography"""
    phenny.say("Hi! I'm Begiak, Apertium's IRC bot.")
    phenny.say("I like to sit around on #apertium and be helpful by letting everyone know about Git commits (and a few other things), and by responding to commands.")
    phenny.say("Check out https://wiki.apertium.org/wiki/Begiak for more info.")
begiak.commands = ['begiak', 'about', 'info']
begiak.priority = 'high'
begiak.example = '.begiak'
