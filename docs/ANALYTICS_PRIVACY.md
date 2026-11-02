# Analytics and privacy preparation

Google Analytics is disabled by default. `nuxt-gtag` uses manual initialization and the Google script is requested only after an explicit analytics consent. The preference is stored locally for six months. Rejecting or closing the banner keeps analytics disabled; the footer and privacy page allow the visitor to reopen the choice. Revocation disables the current tag, attempts to remove first-party GA cookies, and reloads the page. Changes in another tab trigger a reload.

Before enabling this feature:

1. Complete and review `app/pages/privacy.vue` using the actual controller identity, contact details, hosting and server logs, legal bases, retention periods, recipients, international transfers and safeguards, and instructions for exercising rights. Remove the draft notice and `noindex` once the policy is ready for publication.
2. Review the actual GA4 property, data retention, enhanced measurement, linked services, advertising settings, Google contractual terms and transfers. Confirm that these match the policy and the choices presented to visitors. Do not add advertising tags without updating the consent design and policy.
3. Set `NUXT_PUBLIC_ANALYTICS_ID` to the production GA4 measurement ID and `NUXT_PUBLIC_ANALYTICS_POLICY_READY=true` in the production runtime environment. Both are required. Do not set them in development or staging unless deliberately testing with a separate test property.
4. Verify in a clean browser and with developer tools that no Google requests or analytics cookies occur before consent or after rejection, that acceptance works on initial and subsequent visits and navigation, and that revocation stops requests and removes applicable cookies. Test keyboard access, mobile layout, storage restrictions and multiple tabs. Verify real GA4 reporting and its page-view settings separately.

The browser preference is not a server-side consent audit trail. Assess any evidence and retention requirements against the actual deployment. Google cookies can use custom domains or paths; if the tag configuration changes, review the removal routine and verify it in the deployed domain. A failed request or missing local storage never grants analytics consent.
