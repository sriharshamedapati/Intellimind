"""
intent.py — Smart Intent Detector
===================================
Analyzes the student's message and returns which data sources are needed.
This prevents unnecessary API calls and saves Gemini tokens.

Intent categories:
- "maya"        → coding problems, algorithms, code errors, skill tags, programming
- "hoot"        → communication, speaking, listening, reading, writing, LSRW, English
- "memory"      → history, previous sessions, "what did we discuss", "am I improving"
- "performance" → weak areas, progress, score, what to improve
- "placement"   → job interviews, placements, companies, aptitude, resume
- "general"     → greeting, general question, concept explanation (no personal data)
"""

import re

# ── Keyword maps ──
_MAYA_KEYWORDS = [
    # ── Core coding/programming ──
    r"\bcode\b", r"\bcoding\b", r"\bcoder\b",
    r"\bprogram\b", r"\bprogramming\b", r"\bprogrammer\b",
    r"\bdevelop\b", r"\bdeveloper\b", r"\bdev\b",
    r"\bscript\b", r"\bscripting\b",
    r"\bimplementat\b", r"\bimplement\b",
    r"\bbuild\b.*\bapp\b", r"\bapp\b.*\bbuild\b",

    # ── Algorithms & DS ──
    r"\balgorithm\b", r"\balgo\b",
    r"\bdata\s*structure\b", r"\bds\b",
    r"\barray\b", r"\blist\b.*\bdata\b",
    r"\blinked\s*list\b", r"\bdoubly\s*linked\b", r"\bsingly\s*linked\b",
    r"\btree\b", r"\bbinary\s*tree\b", r"\bbst\b", r"\bavl\b", r"\bsegment\s*tree\b", r"\btrie\b",
    r"\bgraph\b", r"\bdirected\b", r"\bundirected\b", r"\bdijkstra\b", r"\bbfs\b", r"\bdfs\b",
    r"\bstack\b", r"\bqueue\b", r"\bdeque\b", r"\bpriority\s*queue\b",
    r"\bhash\b", r"\bhash\s*map\b", r"\bhash\s*table\b", r"\bhash\s*set\b",
    r"\bheap\b", r"\bmin\s*heap\b", r"\bmax\s*heap\b",
    r"\bmatrix\b", r"\bgrid\b",
    r"\bset\b.*\bdata\b", r"\bmap\b.*\bdata\b",

    # ── Sorting & Searching ──
    r"\bsort\b", r"\bsorting\b",
    r"\bbubble\s*sort\b", r"\bmerge\s*sort\b", r"\bquick\s*sort\b",
    r"\binsertion\s*sort\b", r"\bselection\s*sort\b", r"\bheap\s*sort\b",
    r"\bcounting\s*sort\b", r"\bradix\s*sort\b",
    r"\bsearch\b", r"\bsearching\b",
    r"\bbinary\s*search\b", r"\blinear\s*search\b",
    r"\btwo\s*pointer\b", r"\bsliding\s*window\b",

    # ── Problem-solving paradigms ──
    r"\bdynamic\s*programming\b", r"\bdp\b",
    r"\bgreedy\b", r"\bgreedy\s*algorithm\b",
    r"\bbacktrack\b", r"\bbacktracking\b",
    r"\bdivide\s*and\s*conquer\b",
    r"\bmemoiz\b", r"\btabulation\b",
    r"\bbit\s*manipulat\b", r"\bbitwise\b",
    r"\bmath\s*problem\b", r"\bnumber\s*theory\b",
    r"\bprime\b", r"\bsieve\b",

    # ── Recursion & Control flow ──
    r"\brecursion\b", r"\brecursive\b",
    r"\bloop\b", r"\biterat\b",
    r"\bfor\s*loop\b", r"\bwhile\s*loop\b",
    r"\bbreak\b.*\bcontinue\b", r"\bnested\s*loop\b",

    # ── OOP & Language constructs ──
    r"\bfunction\b", r"\bmethod\b", r"\bcallback\b", r"\bclosure\b",
    r"\bclass\b", r"\bobject\b", r"\binstance\b",
    r"\boop\b", r"\bobject\b.*\boriented\b",
    r"\binheritanc\b", r"\bpolymorphism\b", r"\bencapsulat\b", r"\babstract\b",
    r"\binterface\b", r"\boverload\b", r"\boverrid\b",
    r"\bconstructor\b", r"\bdestructor\b",
    r"\bstatic\b.*\bmethod\b", r"\bvirtual\b",
    r"\bdesign\s*pattern\b", r"\bsingleton\b", r"\bfactory\b.*\bpattern\b",

    # ── Languages ──
    r"\bpython\b", r"\bjava\b", r"\bc\+\+\b", r"\bc\b.*\blanguage\b",
    r"\bjavascript\b", r"\bjs\b", r"\btypescript\b", r"\bts\b",
    r"\bkotlin\b", r"\bswift\b", r"\bgo\b.*\blang\b", r"\bgolang\b",
    r"\bruby\b", r"\brust\b", r"\bscala\b", r"\br\b.*\bprogramming\b",
    r"\bphp\b", r"\bperl\b", r"\bmatlab\b",

    # ── Web & Frameworks ──
    r"\bhtml\b", r"\bcss\b",
    r"\breact\b", r"\bvue\b", r"\bangular\b", r"\bsvelte\b",
    r"\bnext\.js\b", r"\bnuxt\b",
    r"\bnode\b", r"\bexpress\b", r"\bfastapi\b", r"\bflask\b", r"\bdjango\b",
    r"\bspring\s*boot\b", r"\bspring\b",
    r"\brest\s*api\b", r"\brestful\b", r"\bgraphql\b", r"\bwebsocket\b",
    r"\bapi\b", r"\bjson\b", r"\bxml\b",
    r"\bhttp\b", r"\bhttps\b", r"\bwebhook\b",

    # ── Databases ──
    r"\bsql\b", r"\bnosql\b", r"\bdatabase\b", r"\bdb\b",
    r"\bquery\b", r"\bjoin\b.*\bsql\b", r"\bindex\b.*\bdb\b",
    r"\bmysql\b", r"\bpostgres\b", r"\bpostgresql\b", r"\bsqlite\b",
    r"\bmongodb\b", r"\bmongo\b", r"\bfirestore\b", r"\bdynamo\b",
    r"\bredis\b", r"\bcassandra\b",
    r"\bnormalizat\b", r"\bschema\b",

    # ── Errors & Debugging ──
    r"\bbug\b", r"\bdebug\b", r"\bdebugging\b",
    r"\bfix\b.*\berror\b", r"\berror\b.*\bfix\b",
    r"\bcompile\b.*\berror\b", r"\bsyntax\s*error\b",
    r"\bruntime\s*error\b", r"\bsegfault\b", r"\bsegmentation\b",
    r"\bexception\b", r"\btry\b.*\bcatch\b", r"\bstack\s*overflow\b",
    r"\bnull\s*pointer\b", r"\bindexerror\b", r"\btypeerror\b",
    r"\bkeyerror\b", r"\bnameerror\b", r"\battributeerror\b",
    r"\bwhy\s*is\s*my\s*code\b", r"\bcode\s*not\s*work\b",
    r"\bcode\s*giving\s*error\b",

    # ── Complexity ──
    r"\bcomplex.*\b", r"\bbig\s*o\b", r"\btime\s*complex\b", r"\bspace\s*complex\b",
    r"\bo\s*\(n\)", r"\bo\s*\(log", r"\boptim\b",

    # ── DevOps & Tools ──
    r"\bgit\b", r"\bgithub\b", r"\bgitlab\b",
    r"\blinux\b", r"\bterminal\b", r"\bcommand\b.*\bline\b", r"\bbash\b", r"\bshell\b",
    r"\bdocker\b", r"\bkubernetes\b", r"\bk8s\b", r"\bci\b.*\bcd\b",
    r"\bcloud\b", r"\baws\b", r"\bazure\b", r"\bgcp\b",

    # ── ML/AI ──
    r"\bmachine\s*learn\b", r"\bml\b.*\bmodel\b", r"\bdeep\s*learn\b",
    r"\bneural\s*net\b", r"\bai\b.*\bmodel\b",
    r"\btraining\b.*\bmodel\b", r"\bclassif\b", r"\bcluster\b", r"\bregression\b",
    r"\bpandas\b", r"\bnumpy\b", r"\bscikitlearn\b", r"\bsklearn\b",
    r"\btensorflow\b", r"\bkeras\b", r"\bpytorch\b",

    # ── Competitive / Practice platforms ──
    r"\bleetcode\b", r"\bhackerrank\b", r"\bcodechef\b", r"\bcodeforces\b",
    r"\bgeeksforgeeks\b", r"\bgfg\b", r"\binterview\s*bit\b",
    r"\bcontest\b", r"\bsubmission\b", r"\baccepted\b.*\bsolution\b",

    # ── Maya platform specific ──
    r"\bmaya\b", r"\bskill\s*tag\b",
    r"\bproblem\b.*\bsolve\b", r"\bsolve\b.*\bproblem\b",
    r"\bhow\s*many\s*problems?\b", r"\bproblems?\s*solved\b",
    r"\bmy\s*submissions?\b", r"\bsubmitted\b.*\bcode\b",

    # ── System Design ──
    r"\bsystem\s*design\b", r"\bhld\b", r"\blld\b",
    r"\bscalab\b", r"\bload\s*balanc\b", r"\bcach\b.*\bsystem\b",
    r"\bmicroservice\b", r"\bmonolith\b",
    r"\bos\b.*\bconcept\b", r"\bthread\b", r"\bprocess\b.*\bos\b",
    r"\bconcurrenc\b", r"\bdeadlock\b", r"\bsemaphor\b",

    # ── Testing ──
    r"\bunit\s*test\b", r"\btest\s*case\b", r"\btesting\b.*\bcode\b",
    r"\bjunit\b", r"\bpytest\b", r"\bmocha\b",

    # ── Memory / pointers ──
    r"\bpointer\b", r"\breference\b.*\bprogramming\b",
    r"\bmemory\s*leak\b", r"\balloc\b", r"\bdealloc\b",
    r"\bstack\b.*\bmemory\b", r"\bheap\b.*\bmemory\b",
]

_HOOT_KEYWORDS = [
    # ── Core LSRW ──
    r"\blsrw\b",
    r"\blistening\b", r"\blisten\b", r"\blistener\b",
    r"\bspeaking\b", r"\bspeak\b", r"\bspeaker\b", r"\bspoke\b",
    r"\breading\b", r"\bread\b.*\bskill\b", r"\bread\b.*\bmodule\b",
    r"\bwriting\b", r"\bwrite\b.*\bskill\b", r"\bwrite\b.*\bmodule\b",
    r"\bwritten\b.*\bskill\b",

    # ── English & Language ──
    r"\benglish\b", r"\bverbal\b", r"\blanguage\s*skill\b",
    r"\bcommunicat\b", r"\bcommunication\b", r"\bcommunicator\b",
    r"\bfluency\b", r"\bfluent\b",
    r"\bvocab\b", r"\bvocabulary\b", r"\bword\s*power\b",
    r"\bgrammar\b", r"\btense\b", r"\bpunctuation\b",
    r"\bspell\b", r"\bspelling\b",
    r"\bsentence\b.*\bstructure\b", r"\bparagraph\b.*\bwrite\b",
    r"\bcomprehension\b", r"\bpassage\b",

    # ── Speaking & Pronunciation ──
    r"\bpronunciat\b", r"\baccent\b", r"\bdiction\b",
    r"\barticul\b", r"\bintonat\b", r"\bpitch\b.*\bvoice\b",
    r"\bpace\b.*\bspeak\b", r"\bclarity\b.*\bspeak\b",
    r"\boral\b", r"\bverbally\b",

    # ── Presentation & Public Speaking ──
    r"\bpresentation\b", r"\bpresent\b.*\bskill\b",
    r"\bpublic\s*speak\b", r"\bstage\s*fright\b",
    r"\bdeliver\b.*\bspeech\b", r"\bspeech\b",
    r"\bdebate\b", r"\bdiscussion\b",

    # ── Interviews & HR ──
    r"\binterview\b.*\bcommunic\b", r"\bhr\s*interview\b",
    r"\bintroduce\s*yourself\b", r"\btell\s*me\s*about\s*yourself\b",
    r"\binterview\s*answer\b", r"\binterview\s*question\b",
    r"\binterview\s*tip\b", r"\binterview\s*skill\b",
    r"\bbehavioral\s*interview\b", r"\bstar\s*method\b",

    # ── Group Discussion ──
    r"\bgroup\s*discuss\b", r"\bgd\b",
    r"\bpanel\s*interview\b",

    # ── Soft Skills & Interpersonal ──
    r"\bsoft\s*skill\b", r"\binterpersonal\b",
    r"\bconfidence\b.*\bspeak\b", r"\bbody\s*language\b",
    r"\bactive\s*listen\b", r"\beyecontact\b", r"\beye\s*contact\b",
    r"\bempathy\b", r"\bemotional\s*intellig\b", r"\beq\b",
    r"\bteamwork\b", r"\bcollaborat\b",
    r"\bnegotiat\b", r"\bpersuasion\b", r"\binfluenc\b.*\bskill\b",
    r"\bconflict\s*resol\b", r"\bleadership\s*communic\b",

    # ── Hoot platform specific ──
    r"\bhoot\b",
    r"\bspeaking\s*module\b", r"\blistening\s*module\b",
    r"\breading\s*module\b", r"\bwriting\s*module\b",
    r"\bmy\s*hoot\b", r"\bhoot\s*score\b", r"\bhoot\s*session\b",
    r"\bhoot\s*progress\b", r"\bhoot\s*practice\b",

    # ── Writing types ──
    r"\bessay\b", r"\bemail\b.*\bwrite\b", r"\bformal\s*letter\b",
    r"\breport\s*write\b", r"\bcover\s*letter\b",
    r"\bresume\b.*\bwrite\b", r"\bcv\b.*\bwrite\b",
    r"\babstract\b.*\bwrite\b",

    # ── Reading skills ──
    r"\bskim\b", r"\bscan\b.*\bread\b", r"\binfer\b.*\bread\b",
    r"\bread\s*speed\b", r"\bspeed\s*read\b",
    r"\bnote\s*tak\b", r"\bsummariz\b",

    # ── Listening skills ──
    r"\bdictation\b", r"\baudio\s*comprehension\b",
    r"\blisten\s*comprehension\b", r"\btranscrib\b",

    # ── Placement communication context ──
    r"\bplacement\s*interview\b.*\bcommunic\b",
    r"\boffcampus\b.*\bcommunic\b", r"\boncampus\b.*\bcommunic\b",
]

_MEMORY_KEYWORDS = [
    # ── Session history ──
    r"\bhistory\b", r"\bprevious\b.*\bsession\b", r"\bsession\s*history\b",
    r"\blast\s*time\b", r"\blast\s*session\b", r"\blast\s*week\b",
    r"\bbefore\b.*\bwe\b", r"\bwe\s*talked\b", r"\bwe\s*discuss\b",
    r"\bwhat\s*did\s*we\b", r"\bwhat\s*we\s*covered\b", r"\bwhat\s*we\s*did\b",
    r"\bwhat\s*topics\s*we\b",

    # ── Memory & recall ──
    r"\bdo\s*you\s*remember\b", r"\bremember\b.*\bearlier\b",
    r"\brecall\b", r"\bwe\s*spoke\b", r"\bwe\s*went\s*over\b",
    r"\bi\s*told\s*you\b", r"\byou\s*told\s*me\b",
    r"\bi\s*asked\s*you\b", r"\byou\s*said\b",

    # ── Progress over time ──
    r"\bam\s*i\s*improv\b", r"\bhave\s*i\s*improv\b",
    r"\bmy\s*progress\b.*\bover\s*time\b",
    r"\btrack\b.*\bprogress\b", r"\bprogress\s*track\b",
    r"\bmy\s*journey\b", r"\bhow\s*far\s*have\s*i\b",
    r"\bhow\s*much\s*have\s*i\b",

    # ── Prior chat references ──
    r"\bprevious\s*chat\b", r"\bearlier\s*convers\b",
    r"\bour\s*last\s*chat\b", r"\bour\s*previous\b",
    r"\bsince\s*last\s*time\b", r"\bfrom\s*last\s*session\b",
    r"\bconversation\s*history\b",

    # ── Activity references ──
    r"\bwhat\s*problems?\b.*\bbefore\b", r"\bproblems?\b.*\bi\s*solved\b.*\bbefore\b",
    r"\bmy\s*old\b.*\bscore\b", r"\bmy\s*earlier\b.*\bscore\b",
    r"\bpast\s*session\b", r"\bprevious\s*week\b",
    r"\byesterday\b.*\bpractice\b", r"\blast\s*month\b.*\bprogress\b",
]

_PERFORMANCE_KEYWORDS = [
    # ── Strengths & Weaknesses ──
    r"\bweak\b", r"\bweakness\b", r"\bweakest\b",
    r"\bstrength\b", r"\bstrongest\b", r"\bstrong\s*area\b",
    r"\bweak\s*area\b", r"\bweak\s*topic\b", r"\bweak\s*in\b",
    r"\bwhat\s*am\s*i\s*weak\b", r"\bwhere\s*am\s*i\s*weak\b",
    r"\bwhat\s*am\s*i\s*bad\b", r"\bwhere\s*do\s*i\s*lack\b",
    r"\bmy\s*gap\b", r"\bknowledge\s*gap\b",

    # ── Progress & Performance ──
    r"\bperformanc\b", r"\bperforming\b",
    r"\bprogress\b", r"\bimprove\b", r"\bimprov\b",
    r"\boverall\b.*\bperform\b", r"\bmy\s*overall\b",
    r"\bhow\s*am\s*i\b", r"\bhow\s*is\s*my\b",
    r"\bhow\s*do\s*i\s*stand\b", r"\bhow\s*am\s*i\s*doing\b",
    r"\bwhere\s*am\s*i\b", r"\bmy\s*level\b",
    r"\bam\s*i\s*good\b", r"\bam\s*i\s*ready\b",

    # ── Scores & Metrics ──
    r"\bscore\b", r"\bmy\s*score\b",
    r"\brating\b", r"\bgrade\b", r"\brank\b",
    r"\bpercentile\b", r"\bbenchmark\b",
    r"\baccount\b.*\bscore\b", r"\btotal\s*score\b",
    r"\bhoot\s*score\b", r"\bmaya\s*score\b",

    # ── What to improve ──
    r"\bwhat\s*(should|do)\s*i\s*improv\b",
    r"\bwhat\s*to\s*improv\b", r"\bneed\s*to\s*improv\b",
    r"\bshould\s*i\s*focus\b", r"\bwhere\s*should\s*i\s*focus\b",
    r"\bwhat\s*to\s*practice\b", r"\bwhat\s*should\s*i\s*practice\b",
    r"\bwhat\s*topics?\s*to\s*study\b", r"\bwhat\s*to\s*study\b",
    r"\bwhat\s*to\s*learn\b", r"\bwhat\s*should\s*i\s*learn\b",
    r"\bsuggest\b.*\btopic\b", r"\brecommend\b.*\btopic\b",
    r"\bnext\s*step\b",

    # ── Assessment & Readiness ──
    r"\bassess\b", r"\bassessment\b", r"\bevaluat\b",
    r"\bplacement\s*ready\b", r"\bready\s*for\s*placement\b",
    r"\binterview\s*ready\b", r"\bready\s*for\s*interview\b",
    r"\bcampus\s*ready\b", r"\bjob\s*ready\b",
    r"\bplacement\s*preparat\b",
    r"\bstatus\b.*\bpreparation\b", r"\bpreparation\s*status\b",

    # ── Comparison & ranking ──
    r"\bcompare\b.*\bmy\s*performance\b",
    r"\bbelow\s*average\b", r"\babove\s*average\b",
    r"\bbetter\s*than\b.*\bother\b",
    r"\bmy\s*ranking\b", r"\bclass\s*rank\b",
]

_PLACEMENT_KEYWORDS = [
    # ── Core Placement ──
    r"\bplacement\b", r"\bjob\b", r"\boffer\b", r"\bcareer\b", r"\bopportunity\b",
    r"\boff\s*campus\b", r"\bon\s*campus\b", r"\bdrive\b", r"\bpool\s*drive\b",
    r"\brecruit\b", r"\brecruitment\b", r"\bhiring\b", r"\bvacanc\b",
    r"\bplacement\s*cell\b", r"\btpo\b", r"\bplacement\s*officer\b",

    # ── Interview Rounds & Stages ──
    r"\binterview\b", r"\brounds?\b", r"\bscreening\b",
    r"\baptitude\b", r"\breasoning\b", r"\bquant\b", r"\blogical\b",
    r"\bgd\b", r"\bgroup\s*discuss\b", r"\bpanel\b",
    r"\boa\b", r"\bonline\s*assessment\b", r"\btest\s*link\b",
    r"\btechnical\s*interview\b", r"\btechnical\s*round\b", r"\btr\b",
    r"\bmanagerial\b", r"\bmr\b", r"\bhr\b", r"\bhr\s*round\b",
    r"\bbehavioral\b", r"\bsituational\b", r"\bmock\s*interview\b",

    # ── Career Documents & Profiles ──
    r"\bresume\b", r"\bcv\b", r"\bcurriculum\s*vitae\b", r"\bportfolio\b",
    r"\bcover\s*letter\b", r"\blinkedin\b", r"\bprofile\b", r"\bsummary\b.*\bresume\b",
    r"\bgithub\b.*\bprofile\b", r"\bprojects?\b.*\bresume\b",

    # ── Company Types ──
    r"\bservice\s*based\b", r"\bproduct\s*based\b", r"\bfaang\b", r"\bmang\b",
    r"\bfintech\b", r"\bedtech\b", r"\bstartup\b", r"\bunicorn\b",
    r"\bmnc\b", r"\bmultinational\b", r"\bfortune\b",

    # ── Specific Companies ──
    r"\btcs\b", r"\btata\s*consultancy\b", r"\bninja\b", r"\bdigital\b", r"\bprime\b",
    r"\bwipro\b", r"\binfosys\b", r"\baccenture\b", r"\bcognizant\b", r"\bcts\b",
    r"\bcapgemini\b", r"\bhcl\b", r"\btech\s*mahindra\b", r"\bibm\b",
    r"\bgoogle\b", r"\bamazon\b", r"\bmicrosoft\b", r"\bmeta\b", r"\bfacebook\b",
    r"\bnetflix\b", r"\bapple\b", r"\badobe\b", r"\boracle\b", r"\bsalesforce\b",
    r"\buber\b", r"\bola\b", r"\bzomato\b", r"\bswiggy\b", r"\bpaytm\b", r"\bflipkart\b",
    r"\bjp\s*morgan\b", r"\bgoldman\s*sachs\b", r"\bmorgan\s*stanley\b", r"\bbarclays\b",

    # ── Salary & Roles ──
    r"\bsalary\b", r"\bpackage\b", r"\blpa\b", r"\bctc\b", r"\bstipend\b",
    r"\bintern\b", r"\binternship\b", r"\bfte\b", r"\bfull\s*time\b",
    r"\bjob\s*role\b", r"\bposition\b", r"\bopening\b", r"\bjob\s*description\b", r"\bjd\b",
    r"\bsde\b", r"\bsoftware\s*engineer\b", r"\banalyst\b", r"\bconsultant\b",

    # ── Preparation ──
    r"\bpreparation\b", r"\bprepare\b.*\bplacement\b", r"\bready\b.*\bplacement\b",
    r"\bhow\s*to\s*crack\b", r"\bcrack\s*the\b", r"\broadmap\b.*\bjob\b",
]

_GENERAL_SIGNALS = [
    # ── Greetings & Closings ──
    r"^(hi|hello|hey|hiya|heya)\b",
    r"^good\s*(morning|afternoon|evening|day|night)\b",
    r"^(thanks|thank\s*you|thx|ty|tysm)\b",
    r"^(bye|goodbye|see\s*you|cya|later)\b",
    r"^(ok|okay|got\s*it|understood|sure|alright)\b",

    # ── Concept / Explanation requests ──
    r"\bexplain\b", r"\bexplanation\b",
    r"\bwhat\s*is\b", r"\bwhat\s*are\b", r"\bwhat\s*does\b",
    r"\bdefine\b", r"\bdefinition\b",
    r"\bhow\s*does\b", r"\bhow\s*do\b", r"\bhow\s*can\b",
    r"\bhow\s*to\b",
    r"\bwhy\s*is\b", r"\bwhy\s*does\b", r"\bwhy\s*do\b",
    r"\bdifference\s*between\b", r"\bcompare\b.*\bconcept\b",
    r"\bvs\b", r"\bversus\b",
    r"\bgive\s*me\s*an?\s*example\b", r"\bfor\s*example\b",
    r"\btell\s*me\s*about\b", r"\btell\s*me\b",
    r"\bcan\s*you\s*explain\b",

    # ── Learning & Study ──
    r"\bwhat\s*should\s*i\s*study\b",
    r"\bwhere\s*to\s*start\b", r"\bhow\s*to\s*start\b",
    r"\blearn\b.*\bfrom\s*scratch\b",
    r"\bbeginner\s*guide\b", r"\bguide\b.*\bbeginner\b",
    r"\blearn\b.*\bfaster\b", r"\btips\b.*\blearn\b",
    r"\bresource\b.*\blearn\b", r"\bbook\b.*\blearn\b",
    r"\bsyllabus\b", r"\bcurriculum\b",

    # ── General questions ──
    r"\bwhat\s*topics\b", r"\bwhich\s*topics\b",
    r"\bhow\s*important\b", r"\bis\s*it\s*necessary\b",
    r"\bdo\s*i\s*need\b", r"\bshould\s*i\b",
    r"\bcan\s*you\s*help\b", r"\bhelp\s*me\s*with\b",
    r"\bi\s*have\s*a\s*question\b", r"\bquestion\s*about\b",
    r"\btell\s*me\s*more\b",

    # ── Motivational / casual ──
    r"\bmotivat\b", r"\bencourag\b",
    r"\bi\s*am\s*stuck\b", r"\bi\s*don'?t\s*understand\b",
    r"\bconfused\b.*\babout\b", r"\bnot\s*getting\b",
    r"\bcan\s*you\s*simplify\b",
]


def _matches(text: str, patterns: list[str]) -> bool:
    """Check if text matches any of the given regex patterns."""
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def detect_intent(message: str) -> list[str]:
    """
    Analyzes the student's message using a weighted scoring system to determine intent.
    This prevents unnecessary data fetching and optimizes context usage.
    """
    msg = message.lower().strip()
    # Remove basic punctuation for cleaner matching
    clean_msg = re.sub(r'[?!.,;:]', '', msg)
    
    scores = {
        "maya": 0,
        "hoot": 0,
        "memory": 0,
        "performance": 0,
        "placement": 0,
        "general": 0
    }

    # 1. Check for personal indicators (boost platform scores)
    personal_patterns = [
        r"\bmy\b", r"\bmine\b", r"\bi\b", r"\bme\b", r"\bam\s*i\b",
        r"\bhow\s*am\s*i\b", r"\bhow\s*is\s*my\b", r"\bmy\s*progress\b",
        r"\bmy\s*score\b", r"\bmy\s*performance\b", r"\bmy\s*level\b"
    ]
    is_personal = _matches(clean_msg, personal_patterns)
    personal_boost = 1.5 if is_personal else 0

    # 2. Check for "pure concept" questions (boost general, suppress platforms)
    concept_patterns = [
        r"^explain\b", r"^what\s*is\b", r"^define\b", r"^how\s*does\b",
        r"^how\s*to\b", r"^tell\s*me\s*about\b", r"^difference\s*between\b",
        r"^what\s*are\b", r"^why\s*is\b", r"^can\s*you\s*explain\b"
    ]
    is_concept = _matches(clean_msg, concept_patterns)
    concept_suppress = 2.0 if (is_concept and not is_personal) else 0

    # 3. Keyword Scoring
    # Helper to count matches
    def get_match_count(text, patterns):
        count = 0
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                count += 1
        return count

    scores["maya"] = get_match_count(clean_msg, _MAYA_KEYWORDS) + personal_boost - concept_suppress
    scores["hoot"] = get_match_count(clean_msg, _HOOT_KEYWORDS) + personal_boost - concept_suppress
    scores["memory"] = get_match_count(clean_msg, _MEMORY_KEYWORDS)
    scores["performance"] = get_match_count(clean_msg, _PERFORMANCE_KEYWORDS)
    scores["placement"] = get_match_count(clean_msg, _PLACEMENT_KEYWORDS)
    scores["general"] = get_match_count(clean_msg, _GENERAL_SIGNALS)

    # 4. Refine Intents
    intents = []
    
    # Threshold-based activation
    if scores["maya"] >= 1: intents.append("maya")
    if scores["hoot"] >= 1: intents.append("hoot")
    if scores["memory"] >= 1: intents.append("memory")
    if scores["performance"] >= 1: intents.append("performance")
    if scores["placement"] >= 1: intents.append("placement")
    
    # Performance queries always need memory context
    if "performance" in intents and "memory" not in intents:
        intents.append("memory")

    # 5. Handle Conflict/Ambiguity
    # If both maya and hoot are present, check if one is significantly stronger
    if "maya" in intents and "hoot" in intents:
        if scores["maya"] > scores["hoot"] + 1:
            intents.remove("hoot")
        elif scores["hoot"] > scores["maya"] + 1:
            intents.remove("maya")

    # 6. Default to General
    if not intents or (scores["general"] > 1 and len(intents) == 0):
        if "general" not in intents:
            intents.append("general")

    # If greeting only, keep it general
    if len(intents) > 1 and scores["general"] > 2 and max(scores["maya"], scores["hoot"]) < 2:
        return ["general"]

    return intents