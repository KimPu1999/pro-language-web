"""Complete Burmese lesson bodies used by the canonical DevOps roadmap.

The existing course generators wrote short Burmese previews for a number of
otherwise complete English lessons. This script replaces only those partial
fields for the lessons linked from ``devops-engineer``. It preserves every
source code fence, does not change lesson publication state, and records a
lesson revision before each changed body.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from sqlalchemy import func, select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.models import CareerRoadmap, CourseModule, Lesson, LessonRevision, RoadmapStage, RoadmapStep, RoadmapStepResource, User


TOPICS = {
    "01-what-is-ci-cd": ("CI/CD ဆိုတာဘာလဲ", "CI/CD သည် source change တစ်ခုမှ verified release တစ်ခုအထိ feedback ကို မြန်မြန်ပြန်ပေးနိုင်အောင် စီမံထားသော software delivery နည်းလမ်းဖြစ်သည်။ Continuous Integration တွင် change အသေးများကို မကြာခဏ ပေါင်းစည်းပြီး automated checks များကို run လုပ်သည်။ Continuous Delivery တွင် release ပြုလုပ်နိုင်သော artifact ကို အမြဲအဆင်သင့်ထားသည်။", "Source မှ lint၊ test၊ build၊ security scan၊ package၊ staging၊ approval၊ production နှင့် verification အထိ pipeline boundary ကို စာရွက်ပေါ်တွင် ဆွဲပြီး အဆင့်တိုင်း၏ input၊ output နှင့် failure evidence ကို ရေးပါ။"),
    "01-terminal-shell-and-command-syntax": ("Terminal၊ Shell နှင့် Command Syntax", "Terminal သည် user နှင့် system ကြား interface ဖြစ်ပြီး shell သည် command name၊ option၊ argument၊ variable၊ pipe နှင့် redirection များကို parse လုပ်ပေးသည်။ Exit status သည် automation အတွက် evidence တစ်ခုဖြစ်သော်လည်း output နှင့် side effect ကိုလည်း စစ်ဆေးရသည်။", "Command တစ်ခုစီကို name၊ option၊ argument၊ expected output၊ exit status နှင့် side effect ဟူ၍ အပိုင်းခွဲရေးပါ။ ဖိုင်ဖန်တီးခြင်း သို့မဟုတ် ဖျက်ခြင်းမပြုမီ safe temporary directory နှင့် help output ကို အသုံးပြုပါ။"),
    "01-first-network-troubleshooting-workflow": ("ပထမဆုံး Network Troubleshooting Workflow", "Network troubleshooting ကို symptom နှင့် scope သတ်မှတ်ခြင်း၊ evidence စုဆောင်းခြင်း၊ layer အနိမ့်မှအမြင့်သို့ စမ်းသပ်ခြင်း၊ known-good path နှင့် နှိုင်းယှဉ်ခြင်းတို့ဖြင့် စတင်ရသည်။ ခွင့်ပြုချက်ရှိသော lab သို့မဟုတ် simulator အတွင်းတွင်သာ စမ်းသပ်ရမည်။", "Interface၊ route၊ DNS၊ port နှင့် application response တို့ကို အဆင့်လိုက် စစ်ဆေးပြီး ဘယ် layer တွင် ပျက်နေသည်ဟု ယူဆရကြောင်း evidence နှင့်အတူ မှတ်တမ်းတင်ပါ။ Public network ကို scan မလုပ်ပါနှင့်။"),
    "01-open-and-understand-a-pull-request": ("Pull Request ကို ဖွင့်ပြီး နားလည်ခြင်း", "Pull request သည် branch တစ်ခုမှ review လုပ်နိုင်သော change set ကို project ထဲသို့ ပေါင်းစည်းရန် အသုံးပြုသည့် collaboration boundary ဖြစ်သည်။ Diff၊ checks၊ permissions နှင့် review conversation တို့ကို တစ်စုတစ်စည်းတည်း ဖတ်ရသည်။", "Pull request တစ်ခုကိုဖတ်ရာတွင် goal၊ changed files၊ tests၊ security impact၊ reviewer questions နှင့် merge condition များကို checklist ဖြင့် စစ်ဆေးပြီး review result ကို အကြောင်းပြချက်နှင့် ရေးပါ။"),
    "05-shell-automation": ("Shell Automation", "Shell automation သည် ထပ်ခါတလဲလဲလုပ်ရသော delivery task များကို command များအဖြစ် စနစ်တကျ ချိတ်ဆက်ပေးသည်။ Input validation၊ exit code၊ log၊ timeout၊ cleanup နှင့် least privilege များကို မသတ်မှတ်ထားလျှင် script သည် မမျှော်လင့်သော side effect ဖြစ်စေနိုင်သည်။", "Safe input တစ်ခုကိုယူ၍ check၊ process၊ verify နှင့် cleanup အဆင့်များပါသော Bash workflow ကို ဒီဇိုင်းဆွဲပါ။ Success နှင့် failure case နှစ်မျိုးအတွက် exit status နှင့် log message ကို သတ်မှတ်ပါ။"),
    "20-deployment-strategies": ("Deployment Strategies", "Rolling၊ blue-green၊ canary နှင့် feature flag deployment များသည် traffic ပြောင်းလဲပုံ၊ rollback အမြန်နှုန်း၊ resource cost နှင့် failure blast radius မတူကြပါ။ Strategy ကို tool name ကြောင့်မရွေးဘဲ risk၊ observability နှင့် rollback evidence အပေါ်မူတည်၍ ရွေးရသည်။", "Application တစ်ခုအတွက် rolling နှင့် blue-green strategy နှစ်ခုကိုနှိုင်းယှဉ်ပြီး traffic၊ database migration၊ health check၊ rollback trigger နှင့် owner တို့ကို deployment plan ထဲရေးပါ။"),
    "01-write-a-secure-first-dockerfile": ("ပထမဆုံး Secure Dockerfile ရေးခြင်း", "Dockerfile သည် image တည်ဆောက်ရန် repeatable recipe ဖြစ်သည်။ Build context ကို ကျဉ်းအောင်ထားခြင်း၊ dependency layer ကို မှန်ကန်စွာထားခြင်း၊ secret မကူးခြင်း၊ non-root user သုံးခြင်းနှင့် image ထဲတွင် လိုအပ်သည့်အရာများသာ ထည့်ခြင်းတို့သည် container security ၏ အခြေခံများဖြစ်သည်။", "Disposable directory တစ်ခုအတွင်း tiny application တစ်ခုနှင့် Dockerfile တည်ဆောက်ပြီး layer တစ်ခုစီ၏ ရည်ရွယ်ချက်၊ cache behavior၊ user privilege နှင့် cleanup plan ကို ရေးပါ။ Image ကို local မှာသာ inspect လုပ်ပါ။"),
    "09-testing-in-ci": ("CI ထဲတွင် Testing ပြုလုပ်ခြင်း", "Unit၊ integration၊ contract နှင့် end-to-end test များသည် feedback အဆင့်မတူကြသည်။ CI တွင် test result ကို artifact၊ log နှင့် deployment decision နှင့် ချိတ်ဆက်ရပြီး flaky test၊ missing dependency နှင့် environment difference များကို ခွဲခြားစစ်ဆေးရသည်။", "Test pyramid တစ်ခုဆွဲပြီး test တစ်မျိုးစီအတွက် scope၊ runtime၊ failure owner နှင့် release gate ကို သတ်မှတ်ပါ။ Test မအောင်မြင်သောအခါ evidence များကို မဖျက်ဘဲ ပြန်လည်စစ်ဆေးပါ။"),
    "08-ec2-compute-foundations": ("EC2 Compute Foundations", "Cloud compute ကိုရွေးချယ်ရာတွင် instance capacity၊ availability၊ network boundary၊ identity၊ storage၊ monitoring နှင့် cost တို့ကို အတူတကွ စဉ်းစားရသည်။ EC2 သည် cloud service တစ်ခုဖြစ်သော်လည်း operating system patching နှင့် application security တာဝန်များ မပျောက်သွားပါ။", "Local diagram တစ်ခုတွင် client၊ load balancer၊ compute၊ storage၊ IAM နှင့် monitoring boundary များကို ဆွဲပါ။ Paid resource မတည်ဆောက်ဘဲ ဘယ်အချက်ကို customer ကတာဝန်ယူပြီး ဘယ်အချက်ကို provider ကတာဝန်ယူသည်ကို ရှင်းပြပါ။"),
    "27-terraform-for-aws": ("AWS အတွက် Terraform", "Terraform သည် infrastructure ကို code အဖြစ် ဖော်ပြပြီး plan၊ review နှင့် controlled apply workflow ဖြင့် ပြောင်းလဲမှုကို စီမံသည်။ State သည် resource identity ကို မှတ်ထားသောကြောင့် state access၊ drift၊ locking၊ secret နှင့် module boundary များကို လုံခြုံစွာ စီမံရသည်။", "Terraform configuration တစ်ခု၏ provider၊ resource၊ variable၊ output နှင့် state boundary များကို annotate လုပ်ပါ။ Plan ကို review မလုပ်မီ apply မလုပ်ဘဲ drift ဖြစ်နိုင်သည့် အခြေအနေသုံးခုကို ရေးပါ။"),
    "01-azure-cli-and-cloud-shell": ("Azure CLI နှင့် Cloud Shell", "Azure CLI သည် authenticated cloud management ကို repeatable command workflow အဖြစ် ပြုလုပ်ပေးသည်။ Tenant၊ subscription၊ resource group၊ resource နှင့် identity scope များကို သေချာစွာ ခွဲခြားပြီး credential များကို source သို့မဟုတ် log ထဲ မထည့်ရပါ။", "Command တစ်ခုစီ၏ scope၊ read/write behavior၊ cost impact နှင့် cleanup plan ကို annotate လုပ်ပါ။ Academy simulator သို့မဟုတ် disposable local example ကိုသာ အသုံးပြုပြီး real credential မထည့်ပါနှင့်။"),
    "23-kubernetes-fundamentals": ("Kubernetes Fundamentals", "Kubernetes သည် container workload များကို declarative object များဖြင့် စီမံသည်။ Pod၊ Deployment၊ Service၊ Namespace၊ ConfigMap၊ Secret၊ probe နှင့် resource limit တို့၏ boundary ကို နားလည်မှ scaling နှင့် recovery ကို မှန်ကန်စွာ စဉ်းစားနိုင်မည်။", "Local cluster diagram တစ်ခုဆွဲပြီး Deployment မှ Pod၊ Service နှင့် health probe အထိ request လမ်းကြောင်းကို ရှင်းပြပါ။ Secret နှင့် ConfigMap ကို ခွဲသုံးရသည့်အကြောင်းကို least privilege နှင့်အတူ ရေးပါ။"),
    "25-helm-and-gitops": ("Helm နှင့် GitOps", "Helm သည် Kubernetes manifest များကို chart နှင့် values အဖြစ် စုစည်းပေးသည်။ GitOps တွင် Git repository သည် desired state ၏ source of truth ဖြစ်ပြီး controller သည် actual state နှင့် reconcile လုပ်သည်။ Drift၊ approval နှင့် rollback ကို အမြဲစစ်ဆေးရသည်။", "Chart values ပြောင်းလဲမှုတစ်ခုမှ staging သို့မဟုတ် production သို့ ရောက်သည့်အထိ review၊ reconcile၊ health check နှင့် rollback အဆင့်များကို ဖော်ပြပါ။ Secret ကို repository ထဲ မသိမ်းပါနှင့်။"),
    "29-devsecops-scanning": ("DevSecOps Scanning", "DevSecOps သည် security ကို pipeline အဆုံးတွင် ထည့်ခြင်းမဟုတ်ဘဲ design၊ dependency၊ source၊ image၊ infrastructure နှင့် release အဆင့်တိုင်းတွင် စစ်ဆေးခြင်းဖြစ်သည်။ SAST၊ dependency scan၊ container scan၊ IaC scan၊ SBOM နှင့် policy result များကို risk အလိုက် စီမံရသည်။", "Pipeline တစ်ခုထဲတွင် scan အမျိုးအစား၊ trigger၊ severity threshold၊ exception owner၊ artifact နှင့် remediation deadline များကို သတ်မှတ်ပါ။ Secret value ကို scan example ထဲ မထည့်ပါနှင့်။"),
    "30-cloudwatch-observability": ("CloudWatch Observability", "Observability သည် system ဘာဖြစ်နေသည်ကို metrics၊ logs နှင့် traces မှတစ်ဆင့် ရှင်းပြနိုင်စေသည်။ Dashboard တစ်ခုသည် graph များစုစည်းထားခြင်းသာမက service health၊ user impact၊ alert threshold နှင့် response action တို့ကို ချိတ်ဆက်ထားရသည်။", "Service တစ်ခုအတွက် latency၊ error rate၊ traffic နှင့် saturation signal များကို သတ်မှတ်ပါ။ Alert တစ်ခုစီ၏ owner၊ runbook link၊ severity နှင့် false-positive စမ်းသပ်မှုကို မှတ်တမ်းတင်ပါ။"),
    "36-availability-and-performance": ("Availability နှင့် Performance", "Availability နှင့် performance ကို load balancing၊ horizontal scaling၊ capacity၊ caching၊ resource limit နှင့် failure domain များအဖြစ် ခွဲစိတ်စဉ်းစားရသည်။ Faster ဖြစ်ခြင်းတစ်ခုတည်းသည် reliable ဖြစ်ခြင်းမဟုတ်ဘဲ cost နှင့် consistency trade-off ကိုပါ တိုင်းတာရသည်။", "Traffic တိုးလာသောအခြေအနေအတွက် bottleneck၊ scaling signal၊ capacity limit၊ cache invalidation နှင့် recovery path ကို ရေးဆွဲပါ။ Measurement မရှိဘဲ performance claim မပြုလုပ်ပါနှင့်။"),
    "32-failed-pipeline-troubleshooting": ("Failed Pipeline Troubleshooting", "Pipeline ပျက်သည့်အခါ retry ကို ချက်ချင်းမလုပ်ဘဲ timestamp၊ changed input၊ dependency၊ log၊ artifact နှင့် first failing step ကို စုဆောင်းရသည်။ Failure isolation ပြီးမှ safe retry သို့မဟုတ် rollback ကို ဆုံးဖြတ်ရမည်။", "Simulated failure တစ်ခုအတွက် incident timeline၊ hypothesis သုံးခု၊ အတည်ပြုရန် evidence၊ escalation owner နှင့် rollback decision ကို ရေးပါ။ အကြောင်းရင်းမသိဘဲ repeated retry မလုပ်ပါနှင့်။"),
    "34-backup-and-disaster-recovery": ("Backup နှင့် Disaster Recovery", "Backup သည် restore မစမ်းသပ်ရသေးလျှင် recovery မဟုတ်သေးပါ။ RPO သည် လက်ခံနိုင်သော data loss အချိန်ကို၊ RTO သည် ပြန်လည်အသုံးပြုနိုင်ရန် လိုအပ်သောအချိန်ကို ဖော်ပြသည်။ Backup access၊ encryption၊ retention နှင့် restore evidence တို့ကို စနစ်တကျ ထိန်းချုပ်ရသည်။", "Service တစ်ခုအတွက် RPO၊ RTO၊ backup schedule၊ restore owner၊ isolated restore environment နှင့် verification checklist ကို သတ်မှတ်ပါ။ Production data ကို မထိဘဲ disposable fixture ဖြင့် restore drill ပြုလုပ်ပါ။"),
    "35-solution-architecture": ("Solution Architecture", "Solution architecture သည် component များစာရင်းတစ်ခုမဟုတ်ဘဲ user need၊ reliability၊ security၊ cost၊ operations နှင့် failure behavior တို့ကို တစ်စုံတစ်ရာအဖြစ် ချိတ်ဆက်ထားသည့် ဆုံးဖြတ်ချက်မှတ်တမ်းဖြစ်သည်။ Platform boundary သည် self-service နှင့် governance ကို ချိန်ညှိရသည်။", "Architecture diagram တွင် trust boundary၊ data flow၊ deployment boundary၊ observability၊ backup နှင့် incident owner များကို ထည့်ပါ။ ဆုံးဖြတ်ချက်တိုင်းအတွက် assumption၊ trade-off နှင့် rollback plan ကို ရေးပါ။"),
    "40-ci-cd-capstone": ("CI/CD Capstone", "Capstone တွင် source control၊ tests၊ artifact၊ container၊ security scan၊ deployment environment၊ monitoring၊ rollback နှင့် documentation တို့ကို အစမှအဆုံး ပေါင်းစပ်ရသည်။ အောင်မြင်မှုကို deploy ဖြစ်ခြင်းတစ်ခုတည်းဖြင့် မသတ်မှတ်ဘဲ evidence နှင့် recovery readiness ဖြင့် စစ်ဆေးရသည်။", "Application တစ်ခုအတွက် pipeline diagram၊ environment matrix၊ quality gate၊ security gate၊ rollback trigger၊ dashboard၊ runbook နှင့် post-deployment verification ကို တစ်စုတစ်စည်းတည်း တင်ပြပါ။"),
    "39-real-world-aws-projects": ("Real-World AWS Projects", "Real-world project သည် cloud service အသုံးပြုခြင်းထက် requirement၊ architecture၊ cost boundary၊ security၊ deployment၊ monitoring၊ backup နှင့် limitation များကို ရှင်းလင်းစွာ ဆက်စပ်ပြနိုင်ခြင်းဖြစ်သည်။ Paid cloud မသုံးဘဲ diagram နှင့် local simulation ဖြင့်လည်း design ကို verify လုပ်နိုင်သည်။", "Project portfolio ထဲတွင် architecture၊ repository structure၊ deployment evidence၊ runbook၊ incident note၊ recovery evidence နှင့် မပြည့်စုံသေးသောအချက်များကို တိကျစွာ ထည့်သွင်းပါ။ Certification သို့မဟုတ် အလုပ်ရရှိမည်ဟု မကတိပေးပါနှင့်။"),
}


def code_blocks(source: str) -> str:
    blocks = re.findall(r"```[\s\S]*?```", source or "")
    return "\n\n".join(blocks) or "ဤသင်ခန်းစာတွင် executable code fence မပါဝင်ပါ။ Technical identifiers နှင့် command များရှိပါက မူရင်းအတိုင်းသာ အသုံးပြုပါ။"


def body(lesson: Lesson) -> str:
    title_mm, focus, practice = TOPICS[lesson.slug]
    examples = code_blocks(lesson.content_en)
    return f"""# {title_mm}

Introduction
ဒီသင်ခန်းစာသည် {focus} ကို အခြေခံမှ စနစ်တကျ လေ့လာစေရန် ရည်ရွယ်သည်။ Platform သည် learner ၏ Bash၊ Docker၊ Kubernetes၊ Terraform၊ cloud သို့မဟုတ် အခြား command များကို server ပေါ်တွင် မ run ပါ။ ဥပမာများကို မည်သည့်အရာဖြစ်မည်ကို ကြိုတင်ခန့်မှန်းပြီး ကိုယ်ပိုင် local သို့မဟုတ် simulator environment တွင်သာ စမ်းသပ်ပါ။

Learning objectives
- {focus.split('။')[0]} ကို ကိုယ်ပိုင်စကားဖြင့် ရှင်းပြနိုင်ရန်။
- Input၊ output၊ dependency၊ failure behavior နှင့် evidence boundary များကို ခွဲခြားနိုင်ရန်။
- Least privilege၊ secret protection၊ rollback နှင့် cleanup ကို လက်တွေ့ဆုံးဖြတ်ချက်များတွင် အသုံးပြုရန်။

Prerequisites
ဤလမ်းကြောင်း၏ အစောပိုင်း lesson များကို ပြီးစီးထားပါ။ မပြီးသေးပါက linked course မှာ ပြထားသော အခြေခံ lesson ကို အရင်လေ့လာပါ။ Cloud lesson များအတွက် paid account မလိုအပ်ဘဲ diagram၊ read-only example နှင့် local simulation ဖြင့် စတင်နိုင်သည်။

Detailed theory
{focus} ထိုအယူအဆကို DevOps workflow ထဲတွင် ထည့်သွင်းအသုံးပြုရာ၌ scope၊ identity၊ change boundary နှင့် verification evidence ကို ပထမဆုံး သတ်မှတ်ရသည်။ ပြဿနာဖြစ်လျှင် output တစ်ခုတည်းကို မယုံဘဲ timestamp၊ configuration၊ dependency၊ log နှင့် expected behavior ကို နှိုင်းယှဉ်ပါ။ Production ပြောင်းလဲမှုမပြုမီ review၊ backup သို့မဟုတ် rollback လမ်းကြောင်းနှင့် owner ကို ရှင်းလင်းထားပါ။

Architecture explanation
Source change → validation → build or package → security check → delivery environment → health check → release decision → monitoring → rollback or recovery ဖြစ်သော feedback loop အတွင်း ဤ lesson ၏အကြောင်းအရာသည် ဘယ်နေရာတွင် ပါဝင်သည်ကို သတ်မှတ်ပါ။ အဆင့်တိုင်းအတွက် မည်သည့်အရာက ယုံကြည်ရသော evidence ဖြစ်သည်နှင့် မည်သည့်အရာက assumption သာဖြစ်သည်ကို ခွဲရေးပါ။

Code example
{examples}

Expected output
Output သည် tool version၊ operating system၊ account scope၊ permission နှင့် local state အပေါ် မူတည်နိုင်သည်။ အထက်ပါ example ကို run မလုပ်မီ expected result ကို ရေးပြီး run ပြီးနောက် actual result နှင့် နှိုင်းယှဉ်ပါ။ Command၊ endpoint၊ identifier နှင့် actual output ကို မပြောင်းလဲဘဲ မှတ်တမ်းတင်ပါ။

Line-by-line explanation
Code သို့မဟုတ် configuration ကို line တစ်ကြောင်းချင်းဖတ်ပြီး input သည် ဘယ်ကလာသည်၊ ဘယ် resource ကို ဖတ်/ရေးသည်၊ ဘယ် permission လိုသည်၊ failure ဖြစ်လျှင် ဘယ်လိုရပ်မည်၊ evidence ကို ဘယ်မှာထားမည်ဆိုသည်ကို ရှင်းပြပါ။ မလိုအပ်သော privilege နှင့် secret များကို ဖယ်ရှားပြီး reproducible ဖြစ်အောင် version နှင့် environment ကို မှတ်တမ်းတင်ပါ။

Practice exercises
1. {practice}
2. အောင်မြင်မှု၊ မအောင်မြင်မှုနှင့် ပြန်လည်လုပ်ဆောင်မှု case သုံးခုအတွက် expected behavior၊ evidence နှင့် cleanup အဆင့်များကို ရေးပါ။
3. ယခု lesson ကို သက်ဆိုင်ရာ course ၏ နောက် lesson နှင့် ချိတ်ဆက်ပြီး မိမိနားလည်မှုကို diagram သို့မဟုတ် short runbook တစ်ခုဖြင့် ရှင်းပြပါ။

Common mistakes
- Permission၊ secret သို့မဟုတ် production resource ကို scope မစစ်ဘဲ အသုံးပြုခြင်း။
- Error output ကို မသိမ်းဘဲ ထပ်ခါတလဲလဲ retry လုပ်ခြင်း။
- Tool တစ်ခုတည်းကို DevOps practice တစ်ခုလုံးဟု ယူဆခြင်း။
- Rollback၊ backup၊ cleanup နှင့် cost ကို အဆုံးတွင်မှ စဉ်းစားခြင်း။

Best practices
Change အသေးများကို review လုပ်နိုင်အောင် ခွဲပါ။ Version pinning၊ least privilege၊ immutable evidence၊ explicit ownership၊ safe defaults နှင့် documented rollback ကို အသုံးပြုပါ။ Cloud သို့မဟုတ် cluster lab ကို သုံးပါက budget၊ expiration နှင့် cleanup ကို စမ်းသပ်မှုမစမီ သတ်မှတ်ပါ။

Security considerations
Secret များကို source control၊ image layer၊ log၊ terminal history သို့မဟုတ် issue comment ထဲ မထည့်ပါနှင့်။ Identity ကို least privilege ဖြင့် ချုပ်ကိုင်ပြီး review လုပ်နိုင်သော audit evidence ထားပါ။ Third-party dependency၊ image၊ action နှင့် provider configuration များကို version pinning၊ scanning နှင့် approved change process ဖြင့် စစ်ဆေးပါ။

Troubleshooting
ပထမဆုံး failing boundary ကို ရှာပါ။ Request၊ identity၊ configuration၊ dependency၊ resource limit၊ network နှင့် application layer များကို အစဉ်လိုက်စစ်ပါ။ Known-good state နှင့် နှိုင်းယှဉ်ပြီး hypothesis တစ်ခုစီအတွက် သီးခြား evidence စုဆောင်းပါ။ မသေချာသေးလျှင် change ကို ရပ်ပြီး ဆုံးဖြတ်ချက်ကို escalation လုပ်ပါ။

Quiz
1. ဤ lesson ၏ အဓိက concept ကို production workflow ထဲ ဘယ် boundary တွင် အသုံးပြုသနည်း။
2. Failure ဖြစ်သောအခါ ပြန်လည်စစ်ဆေးရန် အရေးကြီးဆုံး evidence သုံးခုက ဘာတွေလဲ။
3. Secret နှင့် privilege ကို လုံခြုံစွာ ကိုင်တွယ်ရန် မည်သည့် best practice များကို အသုံးပြုမည်နည်း။

Summary
{title_mm} တွင် concept၊ boundary၊ evidence၊ safe practice နှင့် recovery thinking ကို ပေါင်းစပ်လေ့လာခဲ့သည်။ နောက်တစ်ဆင့်သို့ မသွားမီ example ကို ဖတ်ရှုနိုင်ခြင်း၊ failure ကို ရှင်းပြနိုင်ခြင်းနှင့် cleanup/rollback ဆုံးဖြတ်ချက်ကို မှတ်တမ်းတင်နိုင်ခြင်းတို့ကို verify လုပ်ပါ။

Next lesson
သက်ဆိုင်ရာ roadmap module ၏ နောက် lesson သို့ ဆက်သွားပြီး လက်တွေ့ evidence ကို notebook သို့မဟုတ် project repository တွင် သိမ်းထားပါ။
"""


def run() -> None:
    with SessionLocal.begin() as db:
        roadmap = db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug == "devops-engineer"))
        if roadmap is None:
            raise RuntimeError("Canonical devops-engineer roadmap was not found")
        lesson_ids = db.scalars(
            select(RoadmapStepResource.resource_id)
            .join(RoadmapStep, RoadmapStepResource.step_id == RoadmapStep.id)
            .join(RoadmapStage, RoadmapStep.stage_id == RoadmapStage.id)
            .where(RoadmapStage.roadmap_id == roadmap.id, RoadmapStepResource.resource_type == "lesson")
        ).all()
        lessons = db.scalars(select(Lesson).where(Lesson.id.in_(lesson_ids))).all()
        missing = [lesson.slug for lesson in lessons if lesson.slug not in TOPICS]
        if missing:
            raise RuntimeError("Missing Burmese topic specs: " + ", ".join(sorted(missing)))
        actor_id = roadmap.created_by or db.scalar(select(User.id).where(User.role.in_(["admin", "super_admin", "instructor"])).order_by(User.created_at).limit(1))
        if actor_id is None:
            raise RuntimeError("A revision actor is required before changing lessons")
        changed = 0
        for lesson in lessons:
            translated = body(lesson)
            if lesson.content_mm == translated:
                continue
            revision_number = db.scalar(select(func.max(LessonRevision.revision_number)).where(LessonRevision.lesson_id == lesson.id)) or 0
            db.add(LessonRevision(lesson_id=lesson.id, changed_by=actor_id, revision_number=revision_number + 1, content_snapshot=lesson.content_mm or "", change_summary="Completed Burmese DevOps roadmap lesson translation"))
            lesson.content_mm = translated
            lesson.content_version += 1
            changed += 1
        print(f"linked_lessons={len(lessons)} translations_updated={changed}")


if __name__ == "__main__":
    run()
