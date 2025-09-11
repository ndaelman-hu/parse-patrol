# How to use ELNs

This guide describes how to manually create entries and enter information
via ELNs (electronic lab notebooks). NOMAD ELNs allow you to acquire
consistently structured data from users to augment uploaded files.

!!! warning "Attention"

    This part of the documentation is still work in progress.

## Create a basic ELN entry

Go to `PUBLISH` > `Uploads`. Create a new upload by clicking `CREATE A NEW UPLOAD`
button. This will bring you to the upload page.

Click the `CREATE FROM SCHEMA` button. This will bring-up a dialog for *naming your entry*
and *selecting a schema* for your ELN.
You can use one of NOMAD's built-in schemas or add your own custom schema (see [How to > Customization > How to write a YAML schema package](../customization/elns.md)).

Here we will select the simplest built-in ELN schema, `Basic ELN`.
The `Basic ELN` offers you simple fields for a *name*, *tags*, a *date/time*, and a rich text
editor to enter your notes.
Click on the schema selection box, which will open up a menu with a list of built-in schemas.
Scroll down, find and select `Basic ELN`, add a name for the entry (e.g., "test-ELN:), and click the `CREATE` button in the bottom right of the pop-up dialog box. The full process is illustrated in the following video:

<video width="100%" controls>
  <source src="./images/eln-entry-from-gui.webm" alt="" type="video/mp4">
</video>

Upon entry creation, you will be taken to the `DATA` tab, where you can fill in or edit the predefined ELN quantities in the user-editable ELN interface. Type a dummy description for this entry and then press the :fontawesome-solid-floppy-disk: icon in the upper right. Now, navigate to the `Overview` page to see your changes there.

The editable quantities that you found in your ELN entry (e.g., `short name`, `tags`, `datetime`, `ID`, `description`) appear because they are defined within the `Basic ELN` schema that you selected. NOMAD provides a tool for browsing all such schemas. Go to `ANALYZE > The NOMAD MetaInfo`, then select `nomad > Basic ELN` to view all the quantity definitions and descriptions within this entry class:

<video width="100%" controls>
  <source src="./images/metainfo-browser-basic-eln.webm" alt="" type="video/mp4">
</video>

All the metadata that you enter in your ELN is stored in the structured JSON format according to the corresponding schema.
You can view this JSON by navigating to the `DATA` tab and then clicking on the :fontawesome-solid-cloud-arrow-down: icon. Select the box next to "pretty-print" at the top left for a human-readable view. You can simply copy and paste this content into a JSON file for further use. Alternatively, from the entry, you can download the archive JSON file by navigating to the `FILES` tab and clicking on the :fontawesome-solid-cloud-arrow-down: icon after selecting the file `<entry name>.archive.json`, where `<entry name>` is the name that you entered for this entry.

## Add your own ELN schema

To make NOMAD ELNs more useful, you can define your own schema to create you own data
fields, create more subsections, reference other entries, and much more.

You should have a look at our ELN example upload. Go to `PUBLISH` / `Uploads` and
click the `ADD EXAMPLE UPLOADS` button. The `Electronic Lab Notebook` example, will
contain a schema and entries that instantiate different parts of the schema.
The *ELN example sample (`sample.archive.json`) demonstrates what you can do.

Follow the [How-to write a schema](../customization/basics.md) and [How-to define ELN](../customization/elns.md)
guides to create you own customized of ELNs.

## Integration of third-party ELNs

!!! warning "Attention"

    This part of the documentation is still work in progress.

The code base is part of the [FAIRmat-NFDI](https://github.com/FAIRmat-NFDI/nomad-external-eln-integrations){:target="_
blank"} repository.

NOMAD offers integration with third-party ELN providers, simplifying the process of connecting
and interacting with external platforms. Three main external ELN solutions that are integrated into NOMAD
are: [elabFTW](https://www.elabftw.net/){:target="_blank"}, [Labfolder](https://labfolder.com/){:target="_blank"} and [chemotion](https://chemotion.net/){:target="_blank"}.
The process of data retrieval and data mapping onto NOMAD's schema
varies for each of these third-party ELN provider as they inherently allow for certain ways of communicating with their
database. Below you can find a <b>How-to</b> guide on importing your data from each of these external
repositories.

### elabFTW integration

elabFTW is part of [the ELN Consortium](https://github.com/TheELNConsortium){:target="_blank"}
and supports exporting experimental data in ELN file format. ELNFileFormat is a zipped file
that contains <b>metadata</b> of your elabFTW project along with all other associated data of
your experiments.

<b>How to import elabFTW data into NOMAD:</b>

Go to your elabFTW experiment and export your project as `ELN Archive`. Save the file to your filesystem under
your preferred name and location (keep the `.eln` extension intact).
To parse your ebalFTW data into NOMAD,
go to the upload page of NOMAD and create a new upload. In the `overview` page, upload your exported file (either by
drag-dropping it into the <i>click or drop files</i> box or by navigating to the path where you stored the file).
This causes triggering NOMAD's parser to create as many new entries in this upload as there are experiments in your
elabFTW project.

You can inspect the parsed data of each of your entries (experiments) by going to the <b>DATA</b>
tab of each Entry page. Under <i>Entry</i> column, click on <i>data</i> section. Now a new lane titled
`ElabFTW Project Import` should be visible. Under this section, (some of) the metadata of your project is listed.
There two subsections: 1) <b>experiment_data</b>, and 2) <b>experiment_files</b>.

<b>experiment_data</b> section contains detailed information of the given elabFTW experiment, such as
links to external resources and extra fields. <b>experiment_files</b> section is a list of subsections
containing metadata and additional info of the files associated with the experiment.

### Labfolder integration

Labfolder provides API endpoints to interact with your ELN data. NOMAD makes API calls to
retrieve, parse and map the data from your Labfolder instance/database to a NOMAD's schema.
To do so, the necessary information are listed in the table below:

<i>project_url</i>:
        The URL address to the Labfolder project. it should follow this pattern:
        `https://your-labfolder-server/eln/notebook#?projectIds=your-project-id`. This is used to setup
        the server and initialize the NOMAD schema.

<i>labfolder_email</i>:
        The email (user credential) to authenticate and login the user. <b>Important Note</b>: this
        information <b>is discarded</b> once the authentication process is finished.

<i>password</i>:
        The password (user credential) to authenticate and login the user. <b>Important Note</b>: this
        information <b>is discarded</b> once the authentication process is finished.

<b>How to import Labfolder data into NOMAD:</b>

To get your data transferred to NOMAD, first go to NOMAD's upload page and create a new upload.
Then click on `CREATE ENTRY` button. Select a name for your Entry and pick `Labfolder Project Import` from
the `Built-in schema` dropdown menu. Then click on `CREATE`. This creates an Entry where you can
insert your user information. Fill the `Project url`, `Labfolder email` and `password` fields. Once completed,
click on the `save icon` in the
top-right corner of the screen. This triggers NOMAD's parser to populate the schema of current ELN.
Now the metadata and all files of your Labfolder project should be populated in this Entry.

The `elements` section lists all the data and files in your projects. There are 6 main data types
returned by Labfolder's API: `DATA`, `FILE`, `IMAGE`, `TABLE`, `TEXT` and `WELLPLATE`. `DATA` element is
a special Labfolder element where the data is structured in JSON format. Every data element in NOMAD has a special
`Quantity` called `labfolder_data` which is a flattened and aggregated version of the data content.
`IMAGE` element contains information of any image stored in your Labfolder project. `TEXT` element
contains data of any text field in your Labfodler project.

### Chemotion integration

NOMAD supports importing your data from Chemotion repository via `chemotion` parser. The parser maps
your data that is structured under chemotion schema, into a predefined NOMAD schema. From your Chemotion
repo, you can export your entire data as a zip file which then is used to populate NOMAD schema.

<b>How to import Chemotion data into NOMAD:</b>

Go to your Chemotion repository and export your project. Save the file to your filesystem under
your preferred name and location (`your_file_name.zip`).
To get your data parsed into NOMAD,
go to the upload page of NOMAD and create a new upload. In the `overview` page, upload your exported file (either by
drag-dropping it into the <i>click or drop files</i> box or by navigating to the path where you stored the file).
This causes triggering NOMAD's parser to create one new Entry in this upload.

You can inspect the parsed data of each of this new Entry by navigating to the <b>DATA</b>
tab of the current Entry page. Under <i>Entry</i> column, click on <i>data</i> section. Now a new lane titled
`Chemotion Project Import` should be visible. Under this section, (some of) the metadata of your project is listed.
Also, there are various (sub)sections which are either filled depending on whether your datafile
contains information on them.

If a section contains an image (or attachment) it is appended to the same section under `file` Quantity.

### Openbis integration

Openbis provides API endpoints to interact with your ELN data. NOMAD makes API calls to retrieve, parse, and map the
data from your Openbis instance/database to NOMAD's schema. The necessary information is listed in the table below:

- **project_url**: The URL address to the Openbis project. It should follow this pattern: `https://openbis.example.com`.
  This is used to set up the server and initialize the NOMAD schema.
- **username**: The username (user credential) to authenticate and log in the user. **Important Note**: this information
  **is discarded** once the authentication process is finished.
- **password**: The password (user credential) to authenticate and log in the user. **Important Note**: this information
  **is discarded** once the authentication process is finished.

#### How to Import Openbis Data into NOMAD

To get your data transferred to NOMAD, follow these steps:

1. Go to NOMAD's upload page and create a new upload.
2. Click on the `CREATE ENTRY` button.
3. Select a name for your entry and pick `Openbis Project Import` from the `Built-in schema` dropdown menu.
4. Click on `CREATE`. This creates an entry where you can insert your user information.
5. Fill in the `project url`, `username`, and `password` fields.
6. Once completed, click on the save icon in the top-right corner of the screen. This triggers NOMAD's parser to
   populate the schema of the current ELN. Now, the metadata and all files of your Openbis project should be populated
   in this entry.

The normalizer will search for all entries in your Openbis project and attempt to import them one by one.

### Under Development

The integration of third-party ELNs suite is planned to be moved to a new plug-in mechanism to allow for a smoother
interface for interacting with other ELN providers.
