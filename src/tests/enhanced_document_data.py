"""
Enhanced Document Data for NYC Services GPT MVP

This module provides comprehensive document coverage for all 5 NYC services
to improve the Self-Service Success Rate from 34% to 50-60% for MVP launch.
"""

from typing import List, Dict

def get_enhanced_service_documents() -> List[Dict]:
    """
    Get enhanced document data with comprehensive coverage for all 5 NYC services.
    
    Returns:
        List of document dictionaries with text and service metadata
    """
    documents = []
    
    # Unemployment Benefits - Enhanced Coverage (20 documents)
    unemployment_docs = [
        {
            "text": "How do I apply for unemployment benefits in NYC? You can apply online through the New York State Department of Labor website at labor.ny.gov. You'll need your Social Security number, driver's license, and employment history. The application process typically takes 30 minutes to complete.",
            "service": "unemployment"
        },
        {
            "text": "What documents are required for New York State unemployment? You need proof of identity (Social Security card, driver's license), employment history (W-2 forms, pay stubs), and reason for separation from your job. Keep all documentation organized for the application process.",
            "service": "unemployment"
        },
        {
            "text": "Can I file an unemployment claim online from Staten Island? Yes, you can file online from anywhere in New York State. The online system is available 24/7 and is the fastest way to apply for unemployment benefits. No geographic restrictions apply.",
            "service": "unemployment"
        },
        {
            "text": "What's the processing time for unemployment insurance? Initial claims typically take 2-3 weeks to process. You should receive a determination letter in the mail within this timeframe. Continue certifying weekly while waiting.",
            "service": "unemployment"
        },
        {
            "text": "Who qualifies for partial unemployment benefits? Workers whose hours have been reduced may qualify for partial benefits. You must work less than full-time and earn less than your weekly benefit amount. Report all earnings when certifying.",
            "service": "unemployment"
        },
        {
            "text": "How do I check my weekly unemployment payment status? You can check your payment status online through the NYS Department of Labor website or call the automated phone system. Payments are typically processed within 2-3 business days after certification.",
            "service": "unemployment"
        },
        {
            "text": "What happens if my unemployment claim is denied? If your claim is denied, you have the right to appeal within 30 days. The denial letter will explain the reason and provide appeal instructions. You can continue certifying while appealing.",
            "service": "unemployment"
        },
        {
            "text": "How do I appeal an unemployment benefits decision? You can appeal online, by mail, or by phone within 30 days of the decision. Include any additional documentation that supports your case. An administrative law judge will review your appeal.",
            "service": "unemployment"
        },
        {
            "text": "Are gig workers eligible for unemployment benefits? Yes, gig workers and independent contractors may be eligible for unemployment benefits under certain circumstances. The Pandemic Unemployment Assistance program expanded eligibility for these workers.",
            "service": "unemployment"
        },
        {
            "text": "How do I update my address on my unemployment account? You can update your address online through your NYS Department of Labor account or by calling the unemployment hotline. Keep your contact information current to avoid missing important notices.",
            "service": "unemployment"
        },
        {
            "text": "What is the maximum unemployment benefit amount in NYC? The maximum weekly benefit amount is $504 per week. Your actual benefit amount depends on your earnings in the base period. Benefits are calculated based on your highest quarter of earnings.",
            "service": "unemployment"
        },
        {
            "text": "Can I work part-time while receiving unemployment? Yes, you can work part-time while receiving unemployment benefits. You must report all earnings when certifying weekly. Your benefits will be reduced based on your earnings, but you may still receive partial benefits.",
            "service": "unemployment"
        },
        {
            "text": "How do I report earnings while on unemployment? Report all earnings when certifying weekly online or by phone. Include wages, tips, commissions, and any other income. Failure to report earnings accurately can result in overpayments and penalties.",
            "service": "unemployment"
        },
        {
            "text": "What's 'Extended Duration Benefits' and who qualifies? Extended Duration Benefits provide additional weeks of unemployment when the unemployment rate is high. These benefits are automatically triggered when certain economic conditions are met and are available to eligible claimants.",
            "service": "unemployment"
        },
        {
            "text": "How do I submit my weekly certification for benefits? You can certify weekly online through the NYS Department of Labor website or by phone. Certification is required to receive benefits and must be completed within the designated time period each week.",
            "service": "unemployment"
        },
        {
            "text": "Are independent contractors covered? Independent contractors may be eligible for unemployment benefits under certain circumstances. The Pandemic Unemployment Assistance program expanded eligibility, but regular unemployment insurance typically requires employer contributions.",
            "service": "unemployment"
        },
        {
            "text": "Do I need an SSN to apply? Yes, you need a valid Social Security number to apply for unemployment benefits. If you don't have an SSN, contact the NYS Department of Labor for guidance on alternative documentation options.",
            "service": "unemployment"
        },
        {
            "text": "Can I get retroactive unemployment payments? Retroactive payments may be available in certain circumstances, such as delays in processing or special programs. Contact the NYS Department of Labor directly to inquire about retroactive benefits for your specific situation.",
            "service": "unemployment"
        },
        {
            "text": "Where can I find phone support for unemployment issues? You can call the NYS Department of Labor at 1-888-209-8124 for unemployment assistance. The phone system is available Monday through Friday during business hours.",
            "service": "unemployment"
        },
        {
            "text": "How long do I have to file after losing my job? You should file for unemployment benefits as soon as possible after losing your job. While there's no strict deadline, filing immediately ensures you don't lose any potential benefits and helps expedite the process.",
            "service": "unemployment"
        }
    ]
    documents.extend(unemployment_docs)
    
    # SNAP (Food Stamps) - Enhanced Coverage (20 documents)
    snap_docs = [
        {
            "text": "How do I apply for SNAP benefits in NYC? You can apply online through the NYS Office of Temporary and Disability Assistance website, by phone at 1-800-342-3009, or in person at a local office. The online application is available 24/7 and is the fastest method.",
            "service": "snap"
        },
        {
            "text": "What income limits apply to SNAP in New York? Income limits vary by household size and are updated annually. For a family of four, the gross monthly income limit is approximately $3,250. Net income limits are lower and allow for certain deductions.",
            "service": "snap"
        },
        {
            "text": "Can I pre-screen for SNAP eligibility online? Yes, you can use the pre-screening tool on the NYS Office of Temporary and Disability Assistance website to check if you might qualify before applying. This tool provides an estimate of potential benefits.",
            "service": "snap"
        },
        {
            "text": "What documents do I need for a SNAP interview? You need proof of income (pay stubs, tax returns), identity (photo ID, birth certificate), and residency (utility bills, lease). Bring all documentation to your interview to avoid delays.",
            "service": "snap"
        },
        {
            "text": "How long does SNAP application processing take? Applications are typically processed within 30 days. You may receive benefits retroactively from your application date. Emergency SNAP benefits may be available within 7 days for eligible households.",
            "service": "snap"
        },
        {
            "text": "How do I check my EBT balance? You can check your EBT balance by calling 1-888-328-6399, visiting the EBT website, or checking your last receipt. Your balance is updated after each transaction and is available 24/7.",
            "service": "snap"
        },
        {
            "text": "Can I use EBT at local farmers' markets? Yes, many farmers' markets in NYC accept EBT cards. Look for the 'EBT Accepted' sign at market entrances. Some markets also offer bonus dollars for EBT purchases to encourage healthy eating.",
            "service": "snap"
        },
        {
            "text": "How do I report a change in household size? Report changes in household size within 10 days by calling 1-800-342-3009 or visiting your local office. Changes may affect your benefit amount and eligibility. Keep documentation of household changes.",
            "service": "snap"
        },
        {
            "text": "What happens if my SNAP case is closed? If your SNAP case is closed, you can reapply at any time. Common reasons for closure include missed recertification deadlines, income changes, or failure to provide requested documentation.",
            "service": "snap"
        },
        {
            "text": "How do I reapply for SNAP after denial? You can reapply for SNAP immediately after a denial. Address the reason for the previous denial in your new application. You have the right to appeal a denial within 90 days.",
            "service": "snap"
        },
        {
            "text": "Are college students eligible for SNAP? College students may be eligible for SNAP if they meet certain criteria, such as working 20 hours per week, participating in work-study, or having dependents. Contact your local office for specific eligibility requirements.",
            "service": "snap"
        },
        {
            "text": "How do I appeal a SNAP decision? You can appeal a SNAP decision by requesting a fair hearing within 90 days of the decision. You can request a hearing online, by phone, or in writing. You may continue receiving benefits during the appeal process.",
            "service": "snap"
        },
        {
            "text": "Can mixed-status families apply? Yes, mixed-status families can apply for SNAP benefits. Eligible family members can receive benefits even if some members are not eligible due to immigration status. Only eligible members' income and resources are counted.",
            "service": "snap"
        },
        {
            "text": "What expenses count toward SNAP income deductions? Allowable deductions include shelter costs (rent, utilities), dependent care expenses, medical expenses for elderly/disabled members, and child support payments. These deductions can increase your benefit amount.",
            "service": "snap"
        },
        {
            "text": "How do I find my SNAP case worker's contact? You can find your case worker's contact information by calling 1-800-342-3009 or visiting your local office. Case workers are assigned based on your location and can help with application questions and case management.",
            "service": "snap"
        },
        {
            "text": "How do I request replacement EBT card? You can request a replacement EBT card by calling 1-888-328-6399 or visiting your local office. Replacement cards typically arrive within 5-7 business days. Report lost or stolen cards immediately.",
            "service": "snap"
        },
        {
            "text": "Can I use my SNAP benefits on groceries delivered? Yes, SNAP benefits can be used for grocery delivery from participating retailers. Major grocery chains and online platforms like Amazon Fresh and Instacart accept EBT cards for eligible food items.",
            "service": "snap"
        },
        {
            "text": "Are benefits loaded monthly or biweekly? SNAP benefits are typically loaded monthly on your EBT card. The exact date depends on the last digit of your Social Security number. Benefits are available from the first day of each month.",
            "service": "snap"
        },
        {
            "text": "What outreach programs exist for seniors on SNAP? Seniors can access SNAP through various outreach programs including the Senior SNAP Initiative and partnerships with senior centers and community organizations. These programs provide application assistance and education.",
            "service": "snap"
        },
        {
            "text": "How do I report lost SNAP benefits? Report lost SNAP benefits immediately by calling 1-888-328-6399. You may be able to replace lost benefits if reported within a certain timeframe. Keep records of all transactions and report suspicious activity.",
            "service": "snap"
        }
    ]
    documents.extend(snap_docs)
    
    # Medicaid (Health Coverage) - Enhanced Coverage (20 documents)
    medicaid_docs = [
        {
            "text": "How do I apply for Medicaid in NYC? You can apply online through the NY State of Health marketplace at nystateofhealth.ny.gov, by phone at 1-855-355-5777, or in person at a local office. The online application is available year-round.",
            "service": "medicaid"
        },
        {
            "text": "What income qualifies me for Medicaid? Income limits depend on household size and other factors. For a family of four, the monthly income limit is approximately $3,200. Different limits apply for children, pregnant women, and adults.",
            "service": "medicaid"
        },
        {
            "text": "Can I enroll in Medicaid year-round? Yes, Medicaid enrollment is available year-round. You can apply at any time, not just during open enrollment periods. Coverage typically begins the first day of the month after approval.",
            "service": "medicaid"
        },
        {
            "text": "How do I check my Medicaid application status? You can check online through the NY State of Health website or call the helpline at 1-855-355-5777. You'll need your application ID or Social Security number to check status.",
            "service": "medicaid"
        },
        {
            "text": "What documents are required for Medicaid? You need proof of income (pay stubs, tax returns), identity (photo ID, birth certificate), and residency (utility bills, lease). Citizenship or immigration status documentation may also be required.",
            "service": "medicaid"
        },
        {
            "text": "How do I renew my Medicaid coverage? Medicaid coverage must be renewed annually. You'll receive a renewal notice in the mail. You can renew online, by phone, or by mail. Keep your contact information updated to receive renewal notices.",
            "service": "medicaid"
        },
        {
            "text": "What happens if I miss my renewal deadline? If you miss your renewal deadline, your Medicaid coverage may be terminated. You can reapply immediately, but there may be a gap in coverage. Contact the NY State of Health immediately if you miss the deadline.",
            "service": "medicaid"
        },
        {
            "text": "Can I switch from Emergency Medicaid to full coverage? Yes, you can apply for full Medicaid coverage while on Emergency Medicaid. Full coverage provides more comprehensive benefits. Contact the NY State of Health to begin the application process.",
            "service": "medicaid"
        },
        {
            "text": "How do I add a newborn to my Medicaid plan? You can add a newborn to your Medicaid plan by calling 1-855-355-5777 or updating your case online. Newborns are automatically eligible for Medicaid if the mother is enrolled. Coverage begins from birth.",
            "service": "medicaid"
        },
        {
            "text": "What providers accept Medicaid in Brooklyn? Many healthcare providers in Brooklyn accept Medicaid. You can search for providers online through the NY State of Health website or call 1-855-355-5777 for a list of participating providers in your area.",
            "service": "medicaid"
        },
        {
            "text": "How do I request a Medicaid ID card replacement? You can request a replacement Medicaid ID card by calling 1-855-355-5777 or visiting your local office. Replacement cards typically arrive within 10-14 business days. Keep your card in a safe place.",
            "service": "medicaid"
        },
        {
            "text": "Are dental services covered? Yes, Medicaid covers dental services for children and adults. Covered services include cleanings, fillings, extractions, and emergency dental care. Some services may require prior authorization.",
            "service": "medicaid"
        },
        {
            "text": "How do I appeal a Medicaid denial? You can appeal a Medicaid denial by requesting a fair hearing within 60 days of the decision. You can request a hearing online, by phone, or in writing. You may continue receiving benefits during the appeal process.",
            "service": "medicaid"
        },
        {
            "text": "Can I have Medicaid and marketplace insurance? Generally, you cannot have both Medicaid and marketplace insurance. If you qualify for Medicaid, you should enroll in Medicaid rather than marketplace coverage. Medicaid provides more comprehensive benefits.",
            "service": "medicaid"
        },
        {
            "text": "How do I report a change in income? Report changes in income within 10 days by calling 1-855-355-5777 or updating your case online. Income changes may affect your eligibility and benefit amount. Keep documentation of all income changes.",
            "service": "medicaid"
        },
        {
            "text": "What long-term care services are covered? Medicaid covers long-term care services including nursing home care, home health services, and personal care assistance. These services require prior authorization and may have specific eligibility criteria.",
            "service": "medicaid"
        },
        {
            "text": "How do I find transportation services under Medicaid? Medicaid covers non-emergency medical transportation to appointments. Contact your Medicaid managed care plan or call 1-855-355-5777 to arrange transportation services.",
            "service": "medicaid"
        },
        {
            "text": "What behavioral health services are included? Medicaid covers behavioral health services including mental health counseling, substance abuse treatment, and psychiatric services. Services are provided through participating providers and may require referrals.",
            "service": "medicaid"
        },
        {
            "text": "How do I get language interpretation for Medicaid services? Language interpretation services are available for Medicaid enrollees. You can request an interpreter when scheduling appointments or contact your managed care plan for language assistance services.",
            "service": "medicaid"
        },
        {
            "text": "Can I keep Medicaid if I start working? Yes, you can keep Medicaid while working. Income limits are higher for working individuals and families. Report all income changes to ensure continued eligibility. Some programs provide extended coverage for working families.",
            "service": "medicaid"
        }
    ]
    documents.extend(medicaid_docs)
    
    # Cash Assistance - Enhanced Coverage (20 documents)
    cash_assistance_docs = [
        {
            "text": "How do I apply for Cash Assistance in NYC? You can apply online through the NYS Office of Temporary and Disability Assistance website or in person at a local office. The application process includes an interview and documentation review.",
            "service": "cash_assistance"
        },
        {
            "text": "What's the income cutoff for Family Assistance? Income limits vary by household size and composition. The limits are updated annually and depend on your family's specific circumstances. Contact your local office for current income guidelines.",
            "service": "cash_assistance"
        },
        {
            "text": "How does Safety Net Assistance differ? Safety Net Assistance is for those who don't qualify for Family Assistance. It provides temporary financial support for individuals and families who don't meet the criteria for other assistance programs.",
            "service": "cash_assistance"
        },
        {
            "text": "What documents are needed for a cash assistance interview? You need proof of income (pay stubs, tax returns), identity (photo ID, birth certificate), and residency (utility bills, lease). Additional documentation may be required based on your circumstances.",
            "service": "cash_assistance"
        },
        {
            "text": "How long does approval take? Initial applications are typically processed within 30 days. Emergency grants may be available for urgent situations. The timeline depends on the completeness of your application and required documentation.",
            "service": "cash_assistance"
        },
        {
            "text": "Can I work while on cash assistance? Yes, you can work while receiving cash assistance. There are work requirements and income limits that apply. You must report all earnings and may be required to participate in employment activities.",
            "service": "cash_assistance"
        },
        {
            "text": "How do I report earnings? Report all earnings to your case worker within 10 days of receiving income. Include wages, tips, commissions, and any other income. Accurate reporting is required to maintain eligibility and avoid overpayments.",
            "service": "cash_assistance"
        },
        {
            "text": "What are the work requirements? Cash assistance recipients must participate in work activities unless exempt. Work activities include employment, job search, education, and training programs. Exemptions apply for certain circumstances like caring for young children.",
            "service": "cash_assistance"
        },
        {
            "text": "How do I check my cash assistance payment status? You can check your payment status by calling your case worker or the automated phone system. Payments are typically issued monthly and may be received via direct deposit or EBT card.",
            "service": "cash_assistance"
        },
        {
            "text": "How do I change my bank account for direct deposit? You can update your bank account information by contacting your case worker or visiting your local office. Provide your new account information and routing number for direct deposit setup.",
            "service": "cash_assistance"
        },
        {
            "text": "Can I receive cash assistance for non-citizen household members? Cash assistance eligibility for non-citizens depends on immigration status and other factors. Some non-citizens may be eligible, while others may not qualify. Contact your local office for specific guidance.",
            "service": "cash_assistance"
        },
        {
            "text": "How do I appeal a cash assistance denial? You can appeal a cash assistance denial by requesting a fair hearing within 60 days of the decision. You can request a hearing online, by phone, or in writing. You may continue receiving benefits during the appeal process.",
            "service": "cash_assistance"
        },
        {
            "text": "What sanctions apply for missed appointments? Sanctions may apply for missed appointments or failure to comply with program requirements. Sanctions can result in reduced or suspended benefits. Contact your case worker immediately if you cannot attend an appointment.",
            "service": "cash_assistance"
        },
        {
            "text": "How do I request an emergency cash grant? Emergency cash grants may be available for urgent situations. Contact your local office immediately to request emergency assistance. Documentation of the emergency situation may be required.",
            "service": "cash_assistance"
        },
        {
            "text": "Can I get cash assistance if I'm homeless? Yes, homeless individuals may be eligible for cash assistance. Special provisions apply for homeless applicants, and you may be able to use a shelter address for residency requirements.",
            "service": "cash_assistance"
        },
        {
            "text": "How do I add a child to my case? You can add a child to your cash assistance case by contacting your case worker. Provide the child's birth certificate and other required documentation. The child's needs will be included in your benefit calculation.",
            "service": "cash_assistance"
        },
        {
            "text": "Are utilities included in the budget? Utility costs may be included in your cash assistance budget calculation. The specific amount depends on your household size and actual utility costs. Keep utility bills for documentation.",
            "service": "cash_assistance"
        },
        {
            "text": "How do I find my cash assistance worker's contact? You can find your case worker's contact information by calling your local office or the NYS Office of Temporary and Disability Assistance. Case workers are assigned based on your location.",
            "service": "cash_assistance"
        },
        {
            "text": "What budget deductions apply (e.g. shelter, childcare)? Budget deductions may include shelter costs, childcare expenses, and other allowable expenses. These deductions can increase your benefit amount. Keep documentation of all expenses for your case worker.",
            "service": "cash_assistance"
        },
        {
            "text": "How do I renew my case after closure? You can reapply for cash assistance immediately after case closure. Address the reason for the previous closure in your new application. You may need to provide updated documentation.",
            "service": "cash_assistance"
        }
    ]
    documents.extend(cash_assistance_docs)
    
    # Child Care Subsidy - Enhanced Coverage (20 documents)
    childcare_docs = [
        {
            "text": "How do I apply for child care subsidy in NYC? You can apply online through the NYS Office of Children and Family Services website or contact your local child care resource and referral agency. The application process includes income verification and provider selection.",
            "service": "childcare"
        },
        {
            "text": "What income qualifies for child care assistance? Income limits depend on family size and child care costs. Generally, families earning up to 200% of the federal poverty level may qualify. Income limits are updated annually and vary by region.",
            "service": "childcare"
        },
        {
            "text": "How do I find approved daycare providers? You can search the online provider database through the NYS Office of Children and Family Services website or contact your local child care resource agency for a list of approved providers in your area.",
            "service": "childcare"
        },
        {
            "text": "What documents are required for application? You need proof of income (pay stubs, tax returns), employment (work schedule, employer verification), and child care costs (provider contract, fee schedule). Additional documentation may be required based on your circumstances.",
            "service": "childcare"
        },
        {
            "text": "How long does the approval process take? Applications are typically processed within 30 days. You may receive benefits retroactively from your application date. The timeline depends on the completeness of your application and required documentation.",
            "service": "childcare"
        },
        {
            "text": "Can I keep subsidy if I change providers? Yes, you can transfer your subsidy to a different approved provider. Notify your case worker immediately when changing providers. The new provider must be approved and meet program requirements.",
            "service": "childcare"
        },
        {
            "text": "How do I report a change in work hours? Report changes in work hours to your case worker within 10 days. Changes in work hours may affect your subsidy amount and eligibility. Keep documentation of your work schedule and hours.",
            "service": "childcare"
        },
        {
            "text": "What if my income increases mid-year? Report income increases to your case worker within 10 days. Income changes may affect your subsidy amount and eligibility. Your case will be reviewed and benefits adjusted accordingly.",
            "service": "childcare"
        },
        {
            "text": "How do I check my subsidy payment status? You can check your subsidy payment status by contacting your case worker or the child care resource agency. Payments are typically made directly to approved providers on your behalf.",
            "service": "childcare"
        },
        {
            "text": "Can I use subsidy for after-school programs? Yes, child care subsidies can be used for after-school programs that are approved providers. The program must meet state licensing requirements and be approved by the child care resource agency.",
            "service": "childcare"
        },
        {
            "text": "How do I appeal a subsidy denial? You can appeal a child care subsidy denial by requesting a fair hearing within 60 days of the decision. You can request a hearing online, by phone, or in writing. You may continue receiving benefits during the appeal process.",
            "service": "childcare"
        },
        {
            "text": "Are summer camps covered? Summer camps may be covered if they are approved providers and meet program requirements. Contact your child care resource agency to verify if a specific summer camp is eligible for subsidy payments.",
            "service": "childcare"
        },
        {
            "text": "How do I enroll my child under age 2? Children under age 2 are eligible for child care subsidies. The application process is the same, but you may need to provide additional documentation such as birth certificates and immunization records.",
            "service": "childcare"
        },
        {
            "text": "What co-payments apply? Co-payments are based on family income and size. Families with higher incomes may be required to pay a portion of child care costs. The co-payment amount is calculated when your application is approved.",
            "service": "childcare"
        },
        {
            "text": "How do I find caseworker contact info? You can find your case worker's contact information by calling your local child care resource agency or the NYS Office of Children and Family Services. Case workers are assigned based on your location.",
            "service": "childcare"
        },
        {
            "text": "Can I get emergency child care assistance? Emergency child care assistance may be available for urgent situations. Contact your child care resource agency immediately to request emergency assistance. Documentation of the emergency may be required.",
            "service": "childcare"
        },
        {
            "text": "Is transportation to daycare covered? Transportation to daycare is not typically covered by child care subsidies. However, some programs may provide transportation assistance in certain circumstances. Contact your child care resource agency for specific information.",
            "service": "childcare"
        },
        {
            "text": "How do I renew my subsidy annually? Child care subsidies must be renewed annually. You'll receive a renewal notice in the mail. You can renew online, by phone, or by mail. Keep your contact information updated to receive renewal notices.",
            "service": "childcare"
        },
        {
            "text": "What if my provider stops accepting subsidies? If your provider stops accepting subsidies, you can transfer to a different approved provider. Contact your child care resource agency immediately to find alternative providers in your area.",
            "service": "childcare"
        },
        {
            "text": "Are there priority slots for special-needs children? Yes, priority may be given to children with special needs. Contact your child care resource agency for information about specialized programs and providers that can accommodate special needs.",
            "service": "childcare"
        }
    ]
    documents.extend(childcare_docs)
    
    return documents
