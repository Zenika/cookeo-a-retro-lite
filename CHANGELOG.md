# Changelog

## [0.2.24] - 2024-08-29

### Added

- Add a 404 page is plan_id is not found

### Changed

- Cookie banner is not display anymore when navigating from "Modifier un Ingrédient" button

### Fixed

- Fix font issue for small computer screen with shadow
- Fix boolean behaviour in form
- 'Générique' is correctly pass to objective when not set

## [0.2.23] - 2024-08-29

### Fixed

- Fix retrieving Fields from Firestore instead of Results to send correct values to Front

## [0.2.22] - 2024-08-28

### Added

- Add button of history list of generated retrospective

## [0.2.21] - 2024-08-28

### Added

- Add some themes like Star Wars, Star Trek, Horror, Medieval Fantastic

### Changed

- Improve prompt for more accurate result

## [0.2.20] - 2024-08-27

## Changed

- create json with list of retrospectives

## [0.2.19] - 2024-08-26

### Changed

- Better organisation of the route
- Result route can now take parameter

## [0.2.18] - 2024-08-22

### Fixed 

- Policies consultatoin doen't break the user journey anymore

### Changed

- Use include in html templates for reusability of the code

## [0.2.17] - 2024-08-21

### Added

- Add link for Confidentiality in result page
- Add link for RGPD in result page

### Fixed

- Fix CICD for prod deployment
- Fix link for Confidentiality policy in index page

## [0.2.16] - 2024-08-20

### Added

- Add legal compliance, RGPD link, cookie banner and zenika favicon

## [0.2.15] - 2024-08-19

### Added

- Add anecdotes for Zenika and Gen AI for the waiting page

## [0.2.14] - 2024-08-19

### Added 

- Add some new base workshop and facilitation ideas

### Changed

- Improve prompt to Vertex AI

### Fixed

- CSS for h3
- Contact title level

## [0.2.13] - 2024-08-13

### Added

- Add script to push and deploy on cloud run

## [0.2.12] - 2024-08-13

### Fixed

- Fix for duplicate retros
- Add some anecdotes about Zenika and Generative AI


## [0.2.11] - 2024-08-12

### Added

- Add tag to anecdotes

## [0.2.10] - 2024-08-09

### Fixed

- Fix Duplicate emails

## [0.2.9] - 2024-08-09

### Fixed
- Fix Issue 28 et 29 : Regressions

## [0.2.8] - 2024-08-07

### Changed

- Refactoring Flask Application to separate parameters,config,utils functions in differents modules

## [0.2.7] - 2024-08-06

### Added

- Add Reinit form when reinit button is clicked

## [0.2.6] - 2024-08-02

### Added

- Add Loading Page During Retrospective plan processing

## [0.2.5] - 2024-07-24

### Changed

 - background opacity of body and color of input

### Fixed

- Fix border of invalid input select

## [0.2.4] - 2024-07-22

### Added 

- Selection of the retrospective attendees

## [0.2.3] - 2024-07-19

### Changed

- Use Gemini 1.5-pro model instead of Gemini 1.0-pro for better results
- Zenika logo in mail is a link to Zenika website

### Fixed

- Fix misuse of variable in prompt for objective

## [0.2.2] - 2024-07-19

### Changed

- Change the Cookeo background image to a more kawaii one

## [0.2.1] - 2024-07-19

### Fixed

- Fix Consent checkbox

## [0.2.0] - 2024-07-19

### Added

- Using Firestore to store Retrospective and Users, RGPD compliant

## [0.1.0] - 2024-07-18

### Added

- Initial release of the Cookeo à Rétro application.
- Basic functionality for generating retrospective plans using VertexAI API
- User interface with Materialize CSS.
- Advanced customization options.
- Integration with MailGun API to send retrospective plan to users by email
- Advanced customization options.

### Fixed

- Minor bug fixes and improvements.
