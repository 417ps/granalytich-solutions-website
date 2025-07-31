import { defineStackbitConfig } from '@stackbit/types';
import { GitContentSource } from '@stackbit/cms-git';

export default defineStackbitConfig({
  stackbitVersion: '~0.6.0',
  contentSources: [
    new GitContentSource({
      rootPath: __dirname,
      contentDirs: ['_data'],
      models: [
        {
          name: 'Hero',
          type: 'data',
          file: '_data/hero.yml',
          fields: [
            { name: 'headline', type: 'string', required: true },
            { name: 'subheadline', type: 'text', required: true },
            { name: 'primary_button', type: 'string', required: true },
            { name: 'secondary_button', type: 'string', required: true }
          ]
        },
        {
          name: 'SiteConfig',
          type: 'data',
          file: '_data/site.yml',
          fields: [
            { name: 'company_name', type: 'string', required: true },
            { name: 'tagline', type: 'string', required: true },
            { name: 'phone', type: 'string', required: true },
            { name: 'email', type: 'string', required: true }
          ]
        },
        {
          name: 'Services',
          type: 'data',
          file: '_data/services.yml',
          fields: [
            { name: 'title', type: 'string', required: true },
            { name: 'description', type: 'text', required: true },
            {
              name: 'items',
              type: 'list',
              items: {
                type: 'object',
                fields: [
                  { name: 'name', type: 'string', required: true },
                  { name: 'description', type: 'text', required: true },
                  { name: 'icon', type: 'string', required: true }
                ]
              }
            }
          ]
        },
        {
          name: 'Clients',
          type: 'data',
          file: '_data/clients.yml',
          fields: [
            { name: 'title', type: 'string', required: true },
            {
              name: 'tier1',
              type: 'list',
              items: {
                type: 'object',
                fields: [
                  { name: 'name', type: 'string', required: true },
                  { name: 'logo', type: 'image', required: true },
                  { name: 'alt', type: 'string', required: true }
                ]
              }
            },
            {
              name: 'tier2',
              type: 'list',
              items: {
                type: 'object',
                fields: [
                  { name: 'name', type: 'string', required: true },
                  { name: 'logo', type: 'image', required: true },
                  { name: 'alt', type: 'string', required: true }
                ]
              }
            },
            {
              name: 'tier3',
              type: 'list',
              items: {
                type: 'object',
                fields: [
                  { name: 'name', type: 'string', required: true },
                  { name: 'logo', type: 'image', required: true },
                  { name: 'alt', type: 'string', required: true }
                ]
              }
            }
          ]
        }
      ],
      assetsConfig: {
        referenceType: 'static',
        staticDir: 'uploads',
        uploadDir: 'images',
        publicPath: '/uploads/'
      }
    })
  ]
});